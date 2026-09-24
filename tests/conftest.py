import pytest

from pde_agent_framework.schemas import ExperimentConfig, ExperimentOverview, ProblemSummary


class FakeRunner:
    """Stand-in for agents.Runner that returns a scripted sequence of final_output values.

    Bind FakeRunner(outputs).run to Runner.run via monkeypatch to avoid real LLM
    calls; every awaited Runner.run(...) pops the next output off the queue.
    """

    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.calls = []

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        if not self._outputs:
            raise AssertionError("FakeRunner ran out of scripted outputs.")
        final_output = self._outputs.pop(0)
        usage = type("FakeUsage", (), {"input_tokens": 10, "output_tokens": 5})()
        context_wrapper = type("FakeContextWrapper", (), {"usage": usage})()
        return type("FakeRunResult", (), {"final_output": final_output,
                                          "context_wrapper": context_wrapper})()


@pytest.fixture
def fake_runner():
    return FakeRunner


@pytest.fixture
def problem_summary():
    return ProblemSummary(task="Prove that X holds.",
                          mathematical_objects=["V", "H"],
                          allowed_lemmas_and_theorems=["Hoelder inequality"],
                          assumptions=["f is continuous"],
                          raw_input="raw problem text")


@pytest.fixture
def experiment_overview():
    return ExperimentOverview()


@pytest.fixture
def make_experiment_config():
    def _make(max_reviewer_iterations=3, use_planner_agent=True, output_path="results/dummy/"):
        return ExperimentConfig(max_reviewer_iterations=max_reviewer_iterations,
                                model_name="test-model",
                                use_planner_agent=use_planner_agent,
                                problem_path="problems/dummy.tex",
                                output_path=output_path)
    return _make
