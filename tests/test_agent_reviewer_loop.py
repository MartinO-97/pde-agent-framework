import pytest
from agents import Agent

from pde_agent_framework.schemas import PlannerResult, PlannerReviewerOutput, ProverResult, ProverReviewerOutput
import pde_agent_framework.tools.utils._agent_reviewer_loop as mod

agent_reviewer_loop = mod.agent_reviewer_loop


def spy_constructor(monkeypatch, class_name, captured, capture_key):
    """Wrap mod.class_name so every call is recorded (as a deep copy) before delegating
    to the real class. The deep copy matters because the captured object may be mutated
    in place by later iterations, and we want a snapshot of its state at call time.
    """
    real_cls = getattr(mod, class_name)

    def spy(**kwargs):
        value = kwargs.get(capture_key)
        captured.append(value.model_copy(deep=True) if value is not None else None)
        return real_cls(**kwargs)

    monkeypatch.setattr(mod, class_name, spy)


@pytest.mark.asyncio
async def test_invalid_loop_name_raises_without_calling_agents(monkeypatch, problem_summary,
                                                                experiment_overview, make_experiment_config):
    def fail_if_called(**kwargs):
        raise AssertionError("Runner.run must not be called for an invalid loop_name.")

    monkeypatch.setattr(mod.Runner, "run", fail_if_called)

    with pytest.raises(ValueError):
        await agent_reviewer_loop(Agent(name="main"), Agent(name="reviewer"),
                                  problem_summary, None, make_experiment_config(),
                                  experiment_overview, "not-a-loop")


@pytest.mark.asyncio
async def test_planner_first_iteration_has_no_feedback(monkeypatch, problem_summary,
                                                        experiment_overview, make_experiment_config, fake_runner):
    captured = []
    spy_constructor(monkeypatch, "PlannerInput", captured, "planner_reviewer_feedback")

    fake = fake_runner([
        PlannerResult(plan="step 1"),
        PlannerReviewerOutput(error_description=[], plan_ok=True),
    ])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    await agent_reviewer_loop(Agent(name="planner"), Agent(name="reviewer"),
                              problem_summary, None, make_experiment_config(),
                              experiment_overview, "planner")

    assert captured == [None]


@pytest.mark.asyncio
async def test_planner_second_iteration_receives_previous_feedback(monkeypatch, problem_summary,
                                                                    experiment_overview, make_experiment_config,
                                                                    fake_runner):
    captured = []
    spy_constructor(monkeypatch, "PlannerInput", captured, "planner_reviewer_feedback")

    fake = fake_runner([
        PlannerResult(plan="step 1"),
        PlannerReviewerOutput(error_description=["missing step"], plan_ok=False),
        PlannerResult(plan="step 1, step 2"),
        PlannerReviewerOutput(error_description=[], plan_ok=True),
    ])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    await agent_reviewer_loop(Agent(name="planner"), Agent(name="reviewer"),
                              problem_summary, None, make_experiment_config(max_reviewer_iterations=5),
                              experiment_overview, "planner")

    assert captured[0] is None
    assert captured[1] is not None
    assert captured[1].error_description == ["missing step"]


@pytest.mark.asyncio
async def test_loop_stops_as_soon_as_reviewer_approves(monkeypatch, problem_summary,
                                                        experiment_overview, make_experiment_config, fake_runner):
    fake = fake_runner([
        PlannerResult(plan="step 1"),
        PlannerReviewerOutput(error_description=[], plan_ok=True),
    ])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    await agent_reviewer_loop(Agent(name="planner"), Agent(name="reviewer"),
                              problem_summary, None, make_experiment_config(max_reviewer_iterations=5),
                              experiment_overview, "planner")

    assert len(fake.calls) == 2
    assert experiment_overview.planner_reviewer_iterations == 1


@pytest.mark.asyncio
async def test_loop_stops_at_max_iterations_if_never_approved(monkeypatch, problem_summary,
                                                               experiment_overview, make_experiment_config,
                                                               fake_runner):
    fake = fake_runner([
        PlannerResult(plan="p"), PlannerReviewerOutput(error_description=["e"], plan_ok=False),
        PlannerResult(plan="p"), PlannerReviewerOutput(error_description=["e"], plan_ok=False),
    ])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    _, history = await agent_reviewer_loop(Agent(name="planner"), Agent(name="reviewer"),
                                           problem_summary, None, make_experiment_config(max_reviewer_iterations=2),
                                           experiment_overview, "planner")

    assert experiment_overview.planner_reviewer_iterations == 2
    assert history.plan_ok is False


@pytest.mark.asyncio
async def test_reviewer_output_type_mismatch_raises(monkeypatch, problem_summary,
                                                     experiment_overview, make_experiment_config, fake_runner):
    fake = fake_runner([
        PlannerResult(plan="p"),
        ProverReviewerOutput(error_description=[], proof_ok=True),  # wrong type for a planner loop
    ])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    with pytest.raises(ValueError):
        await agent_reviewer_loop(Agent(name="planner"), Agent(name="reviewer"),
                                  problem_summary, None, make_experiment_config(),
                                  experiment_overview, "planner")


@pytest.mark.asyncio
async def test_prover_loop_only_updates_prover_counter(monkeypatch, problem_summary,
                                                        experiment_overview, make_experiment_config, fake_runner):
    fake = fake_runner([
        ProverResult(proof="...", proof_name="Theorem"),
        ProverReviewerOutput(error_description=[], proof_ok=True),
    ])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    plan = PlannerResult(plan="step 1")
    main_result, history = await agent_reviewer_loop(Agent(name="prover"), Agent(name="reviewer"),
                                                      problem_summary, plan, make_experiment_config(),
                                                      experiment_overview, "prover")

    assert experiment_overview.prover_reviewer_iterations == 1
    assert experiment_overview.planner_reviewer_iterations == 0
    assert main_result.proof_name == "Theorem"
    assert history.proof_ok is True
