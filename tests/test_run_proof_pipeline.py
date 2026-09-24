import pytest

from pde_agent_framework.schemas import ExperimentOverview, PlannerResult, ProverResult
import pde_agent_framework.tools.utils._run_proof_pipeline as mod

run_proof_pipeline = mod.run_proof_pipeline


@pytest.mark.asyncio
async def test_raises_if_load_config_was_not_called(monkeypatch, make_experiment_config):
    def fail_if_called(**kwargs):
        raise AssertionError("No agent should run before the load_config guard fires.")

    monkeypatch.setattr(mod.Runner, "run", fail_if_called)

    overview = ExperimentOverview()  # load_config() never called

    with pytest.raises(ValueError):
        await run_proof_pipeline(make_experiment_config(), overview)


@pytest.mark.asyncio
async def test_raises_if_extractor_output_is_not_problem_summary(monkeypatch, make_experiment_config,
                                                                  experiment_overview, fake_runner):
    config = make_experiment_config()
    experiment_overview.load_config(config)

    fake = fake_runner(["not-a-problem-summary"])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    with pytest.raises(ValueError):
        await run_proof_pipeline(config, experiment_overview)


@pytest.mark.asyncio
async def test_planner_skipped_when_use_planner_agent_false(monkeypatch, problem_summary, make_experiment_config,
                                                             experiment_overview, fake_runner, tmp_path):
    config = make_experiment_config(use_planner_agent=False, output_path=f"{tmp_path}/")
    experiment_overview.load_config(config)

    fake = fake_runner([problem_summary, "latex proof"])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    prover_result = ProverResult(proof="...", proof_name="Theorem")
    calls = []

    async def fake_loop(**kwargs):
        calls.append(kwargs)
        return prover_result, None

    monkeypatch.setattr(mod, "agent_reviewer_loop", fake_loop)

    await run_proof_pipeline(config, experiment_overview)

    assert len(calls) == 1
    assert calls[0]["loop_name"] == "prover"
    assert calls[0]["plan"] == PlannerResult(plan="")


@pytest.mark.asyncio
async def test_planner_then_prover_when_use_planner_agent_true(monkeypatch, problem_summary, make_experiment_config,
                                                                experiment_overview, fake_runner, tmp_path):
    config = make_experiment_config(use_planner_agent=True, output_path=f"{tmp_path}/")
    experiment_overview.load_config(config)

    fake = fake_runner([problem_summary, "latex proof"])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    planner_result = PlannerResult(plan="step 1")
    prover_result = ProverResult(proof="...", proof_name="Theorem")
    calls = []

    async def fake_loop(**kwargs):
        calls.append(kwargs["loop_name"])
        return (planner_result, None) if kwargs["loop_name"] == "planner" else (prover_result, None)

    monkeypatch.setattr(mod, "agent_reviewer_loop", fake_loop)

    await run_proof_pipeline(config, experiment_overview)

    assert calls == ["planner", "prover"]
    assert experiment_overview.proof == "latex proof"


@pytest.mark.asyncio
async def test_raises_if_planner_result_has_wrong_type(monkeypatch, problem_summary, make_experiment_config,
                                                        experiment_overview, fake_runner):
    config = make_experiment_config(use_planner_agent=True)
    experiment_overview.load_config(config)

    fake = fake_runner([problem_summary])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    async def fake_loop(**kwargs):
        return "not-a-planner-result", None

    monkeypatch.setattr(mod, "agent_reviewer_loop", fake_loop)

    with pytest.raises(ValueError):
        await run_proof_pipeline(config, experiment_overview)


@pytest.mark.asyncio
async def test_writes_proof_and_overview_to_disk(monkeypatch, problem_summary, make_experiment_config,
                                                  experiment_overview, fake_runner, tmp_path):
    output_path = f"{tmp_path}/"
    config = make_experiment_config(use_planner_agent=False, output_path=output_path)
    experiment_overview.load_config(config)

    fake = fake_runner([problem_summary, "\\documentclass{article}..."])
    monkeypatch.setattr(mod.Runner, "run", fake.run)

    prover_result = ProverResult(proof="...", proof_name="Theorem")

    async def fake_loop(**kwargs):
        return prover_result, None

    monkeypatch.setattr(mod, "agent_reviewer_loop", fake_loop)

    await run_proof_pipeline(config, experiment_overview)

    tex_files = list(tmp_path.glob("*.tex"))
    overview_files = list(tmp_path.glob("*_overview.json"))

    assert len(tex_files) == 1
    assert len(overview_files) == 1
    assert tex_files[0].read_text() == "\\documentclass{article}..."
    assert "\"model_name\": \"test-model\"" in overview_files[0].read_text()
