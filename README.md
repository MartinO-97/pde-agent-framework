# pde-agent-framework

## Pipeline Overview

The framework turns a mathematical problem statement (a `.tex` file) into a finished
LaTeX proof through four stages: an agent first **extracts** the task, objects,
assumptions, and allowed tools into a structured `ProblemSummary`; a `PlannerAgent` then
optionally **plans** a proof outline, refining it against a `PlannerReviewerAgent`'s
feedback until the plan is approved or the iteration budget runs out; a `ProverAgent`
**proves** the theorem from that plan (or from the problem alone, if planning was
skipped), again refined against a `ProverReviewerAgent`; and finally a `WriterAgent`
**writes** the accepted proof as compilable LaTeX, alongside a JSON overview of the run
(iteration counts, token usage, model used).

```mermaid
flowchart TD
    A(["problem .tex file"]) --> B["ProblemSpecificationAgent"]
    B --> C[/"ProblemSummary"/]
    C --> D{"use_planner_agent?"}

    D -- yes --> E
    D -- no --> H["empty PlannerResult"]

    subgraph E ["Plan loop"]
        direction TB
        E1["PlannerAgent"] --> E2["PlannerReviewerAgent"]
        E2 -- "plan_ok = False" --> E1
    end

    E -- "plan_ok = True" --> F[/"PlannerResult"/]
    E -- "max_reviewer_iterations reached" --> F
    H --> F

    F --> G

    subgraph G ["Prove loop"]
        direction TB
        G1["ProverAgent"] --> G2["ProverReviewerAgent"]
        G2 -- "proof_ok = False" --> G1
    end

    G -- "proof_ok = True" --> I[/"ProverResult"/]
    G -- "max_reviewer_iterations reached" --> I
    I --> J["WriterAgent"]
    J --> K([".tex + _overview.json"])
```

Both review loops are the same `agent_reviewer_loop` function, parameterized by
`loop_name`; they stop early on approval or once `max_reviewer_iterations` is reached.

## Running the Experiments

**Prerequisites**
- Python 3.13+
- `pip install -r requirements.txt`
- An OpenAI API key with access to whichever model you want to use

**Setup**
1. Copy `.env.example` to `.env`.
2. Fill in `OPENAI_API_KEY` and set `MODEL_NAME` to the model you want to run against.

**Run**

`src/pde_agent_framework/experiments/run_experiment.py` runs a single Extract -> maybe
Plan -> Prove -> Write pass over one problem file and writes the results (`.tex` +
`_overview.json`) to the given output directory. Pass `--planner` to employ the
PlannerAgent-PlannerReviewerAgent loop; omit it to skip straight to proving. From the
repo root:

```bash
# with the planner-reviewer loop
PYTHONPATH=src python3 -m pde_agent_framework.experiments.run_experiment \
    problems/Parabolic_Estimator/parabolic_estimator.tex results/Parabolic_Estimator/ --planner

# without it
PYTHONPATH=src python3 -m pde_agent_framework.experiments.run_experiment \
    problems/Parabolic_Estimator/parabolic_estimator.tex results/Parabolic_Estimator/
```

Run it twice (with and without `--planner`) to reproduce the side-by-side comparison
below. To try a different problem, just add a `.tex` file describing it under
`problems/` and point the command at it — no code changes needed.

## Model Comparison

`ExperimentConfig` and `ExperimentOverview` were designed from the start to make reviewer
convergence (iterations per review loop) and cost (input/output tokens) first-class,
measurable outputs of every run, rather than something only visible by reading logs.
That made it possible to run a direct, apples-to-apples comparison across models and
pipeline configurations, instead of a one-off "it worked" demonstration.

Both experiments (Ceas Lemma Proof, Parabolic Estimator) were run with two models,
gpt-6-sol and gpt-5.4-nano, each with and without the PlannerAgent-PlannerReviewerAgent
loop enabled, to compare cost and convergence behavior. All runs carried out so far:

| Problem | Model | Planner | Planner iters | Prover iters | Input / Output tokens | Proof correct? | Notes |
|---|---|---|---|---|---|---|---|
| Ceas Lemma | gpt-6-sol | yes | 2 | 1 | 16,072 / 5,021 | TBD | before the coercivity-assumption typo was fixed |
| Ceas Lemma | gpt-6-sol | no | — | 1 | 7,377 / 3,061 | TBD | before the coercivity-assumption typo was fixed |
| Ceas Lemma | gpt-6-sol | yes | 1 | 1 | 11,920 / 3,415 | TBD | |
| Ceas Lemma | gpt-6-sol | no | — | 1 | 7,539 / 3,085 | TBD | |
| Ceas Lemma | gpt-5.4-nano | yes | 5 (capped) | 1 | 35,231 / 9,291 | TBD | |
| Ceas Lemma | gpt-5.4-nano | no | — | 5 (capped) | 30,941 / 9,042 | TBD | |
| Parabolic Estimator | gpt-6-sol | yes | 1 | 1 | 35,268 / 11,972 | TBD | |
| Parabolic Estimator | gpt-6-sol | no | — | 1 | 21,625 / 11,591 | TBD | |
| Parabolic Estimator | gpt-6-sol | yes | 1 | 1 | 35,932 / 14,424 | TBD | repeat run |
| Parabolic Estimator | gpt-6-sol | no | — | 2 | 36,347 / 15,360 | TBD | repeat run |
| Parabolic Estimator | gpt-5.4-nano | yes | 5 (capped) | 5 (capped) | 128,593 / 38,246 | TBD | |
| Parabolic Estimator | gpt-5.4-nano | no | — | 5 (capped) | 58,788 / 22,120 | TBD | |

"Proof correct?" reflects a manual mathematical review of each generated proof against
the stated theorem, not an automated check — pending review.

gpt-6-sol consistently converges (its own reviewer approves the plan/proof) within 1-2
iterations. gpt-5.4-nano instead hits the `max_reviewer_iterations` cap in almost every
run; since each additional iteration resends the accumulated feedback history, this is
also what drives its 3-4x higher token cost on the harder Parabolic Estimator problem.

## Future Work

- Design an implementation pipeline that takes the theoretical results produced by the
  proof pipeline and verifies them numerically on suitable examples.
- Persist the PlannerReviewer/ProverReviewer feedback history to disk, so that
  runs which exhaust max_reviewer_iterations without approval can be debugged after
  the fact instead of only being visible as a raw iteration count.
