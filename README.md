# pde-agent-framework

**pde-agent-framework** is a multi-agent LLM pipeline that turns a formal mathematical
problem statement into a rigorous, LaTeX-typeset proof — orchestrating specialized
agents that extract the problem, plan a proof strategy, write the proof, and critically
review each step against the stated assumptions. Beyond just generating proofs, the
framework was designed from the ground up to make its own cost and convergence behavior
measurable, enabling direct, apples-to-apples comparisons across models and pipeline
configurations (see [Model Comparison](#model-comparison)).

## Key Findings

- **gpt-6-sol converges reliably**: its own reviewer approves the plan/proof within 1-3
  iterations in 7 of 8 runs. **gpt-5.4-nano exhausts the iteration cap in all 4 of its
  runs**, and uses up to ~4x more tokens as a direct result — a cheaper, older model
  isn't necessarily cheaper in practice.
- **The planner agent had no measurable effect on correctness** in these experiments —
  runs with and without it were correct about equally often — only on iteration count
  and cost.
- **A recurring mathematical error was independently caught and verified**: two
  gpt-6-sol proofs incorrectly claimed a regularity hypothesis couldn't be established
  for a piecewise-affine reconstruction function; the actual reason is elementary (see
  [Parabolic Estimator Deep Dive](#parabolic-estimator-deep-dive)).

**Tech stack**: OpenAI Agents SDK · Pydantic · pytest · argparse · Docker / Dev Containers

## Table of Contents

- [Key Findings](#key-findings)
- [Pipeline Overview](#pipeline-overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Tests](#tests)
- [Running the Experiments](#running-the-experiments)
- [Model Comparison](#model-comparison)
  - [Problem Independent Results](#problem-independent-results)
  - [Cea's Lemma Deep Dive](#ceas-lemma-deep-dive)
  - [Parabolic Estimator Deep Dive](#parabolic-estimator-deep-dive)
- [Future Work](#future-work)
- [Acknowledgments](#acknowledgments)
- [License](#license)

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

## Project Structure

```
src/pde_agent_framework/
├── agent_systems/   # Agent definitions: ProblemSpecificationAgent, PlannerAgent,
│                    # PlannerReviewerAgent, ProverAgent, ProverReviewerAgent, WriterAgent
├── schemas/         # Pydantic I/O contracts between pipeline stages (ProblemSummary,
│                    # PlannerResult, ProverResult, ExperimentConfig, ExperimentOverview, ...)
├── tools/
│   ├── agent_tools/ # @function_tool functions exposed to agents (e.g. load_problem_file)
│   └── utils/       # Orchestration logic: agent_reviewer_loop, run_proof_pipeline
└── experiments/     # CLI entrypoint: run_experiment.py

problems/            # Problem statements (.tex) to feed into the pipeline
results/             # Default output folder for generated proofs and run overviews
docs/results/        # Frozen copies of the runs discussed in the Model Comparison (.tex, .pdf, .json)
tests/               # pytest suite
```

## Installation

**Option A: Dev Container**

The repo ships a [`.devcontainer`](.devcontainer/devcontainer.json) config built on the
provided [`Dockerfile`](Dockerfile) (Python 3.13, with `requirements.txt` installed at
image build time). With Docker and the VS Code "Dev Containers" extension installed,
open the repo in VS Code and choose "Reopen in Container" — the image is built and every
dependency is ready, no local Python setup needed.

**Option B: Bare metal**

Install directly on your own machine (Python 3.13+ required):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Tests

Either way, verify the installation with the test suite:

```bash
pytest tests/
```

`pyproject.toml` already points pytest at `src/`, so no `PYTHONPATH` is needed here —
unlike running the experiment script directly, see below.

## Running the Experiments

**Prerequisites**
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

Both experiments (Cea's Lemma Proof, Parabolic Estimator) were run with two models,
gpt-6-sol and gpt-5.4-nano, each with and without the PlannerAgent-PlannerReviewerAgent
loop enabled, to compare cost and convergence behavior. All runs carried out so far;
"Result" is the timestamp identifying the corresponding files under
[`docs/results/<Problem>/`](docs/results) (`<timestamp>.pdf` for the readable proof,
`<timestamp>.tex`, `<timestamp>_overview.json`):

| Problem | Model | Planner | Planner iters | Prover iters | Input / Output tokens | Proof correct? | Result |
|---|---|---|---|---|---|---|---|
| Cea's Lemma | gpt-6-sol | yes | 2 | 1 | 16,072 / 5,021 | yes | 20260925_094812 |
| Cea's Lemma | gpt-6-sol | no | — | 1 | 7,377 / 3,061 | yes | 20260925_094853 |
| Cea's Lemma | gpt-6-sol | yes | 1 | 1 | 11,920 / 3,415 | yes | 20260925_101906 |
| Cea's Lemma | gpt-6-sol | no | — | 1 | 7,539 / 3,085 | yes | 20260925_101943 |
| Cea's Lemma | gpt-5.4-nano | yes | 5 (capped) | 1 | 35,231 / 9,291 | yes | 20260926_105435 |
| Cea's Lemma | gpt-5.4-nano | no | — | 5 (capped) | 30,941 / 9,042 | yes (with reservations) | 20260926_105535 |
| Parabolic Estimator | gpt-6-sol | yes | 2 | 1 | 47,835 / 16,146 | yes (with reservations) | 20260928_115447 |
| Parabolic Estimator | gpt-6-sol | no | — | 5 (capped) | 78,000 / 35,607 | yes (with reservations) | 20260928_120856 |
| Parabolic Estimator | gpt-6-sol | yes | 2 | 3 | 77,174 / 17,143 | yes | 20260928_125327 |
| Parabolic Estimator | gpt-6-sol | no | — | 1 | 21,522 / 10,944 | yes | 20260928_130122 |
| Parabolic Estimator | gpt-5.4-nano | yes | 5 (capped) | 5 (capped) | 176,283 / 36,055 | no | 20260928_130604 |
| Parabolic Estimator | gpt-5.4-nano | no | — | 5 (capped) | 93,587 / 25,938 | yes (with reservations) | 20260928_130945 |

"Proof correct?" reflects a manual mathematical review of each generated proof against
the stated theorem, not an automated check — all twelve runs have been reviewed;
see the deep dives below for the reasoning behind each verdict.

### Problem Independent Results 

gpt-6-sol converges (its own reviewer approves the plan/proof) within the iteration
budget in nearly every run — 7 of the 8 gpt-6-sol runs finish in 1-3 iterations without
hitting the cap. The one exception, `20260928_120856` on the harder Parabolic Estimator
problem, still exhausted the cap while constructing the flawed regularity argument
discussed below. **gpt-5.4-nano, in contrast, exhausts the `max_reviewer_iterations`
cap in every single run conducted so far** (4 of 4) — its own reviewer essentially never
approves a plan or proof within the allotted budget, on either problem.

As a direct consequence, **gpt-5.4-nano's token usage is significantly larger than
gpt-6-sol's** on both problems, since each additional iteration resends the accumulated
feedback history — roughly 1.2-4x more input tokens across the matched configurations,
depending on the problem (the low end of that range is driven by `20260928_120856`,
gpt-6-sol's own atypical capped run; against gpt-6-sol's typical, uncapped runs the
multiplier is closer to 2-4x). In these experiments, the cheaper, older model ended up
more expensive overall: when it fails to converge within the review budget, the
resulting iteration overhead can outweigh the per-token savings of a stronger, pricier
model that gets it right on the first or second try.

Across all twelve experiments, employing the planner agent does not appear to have much influence on whether
the final proof is correct. Of the six planner-enabled runs, five are correct (one with reservations) and one
— `20260928_130604` (gpt-5.4-nano) — is not; of the six no-planner runs, all six are correct, three of them
with reservations. If anything, in this small sample, skipping the planner did not increase the error rate;
its main measurable effect so far is on iteration count and cost, not on final correctness.

### Cea's Lemma Deep Dive

Analyzing the Cea's Lemma experiments, we see that all generated proofs were correct. However, in the `20260926_105535` experiment, there is one
little inaccuracy. Therein, the following is written: "fix a finite-dimensional subspace". However, `ceas_lemma_proof.tex` explicitly defines
a concrete finite-dimensional subspace of the Sobolev space.

The experiments in the first two rows were conducted with a typo in the
`ceas_lemma_proof.tex` concerning the coercivity condition. To be precise, the coercivity condition
for the first two experiments were defined as
```math
\begin{gather*}
     a\left(u, v\right) \geq c \left\| u \right\|_{1,\Omega}^2 \quad \text{for all } u,v \in H^1_0(\Omega).
\end{gather*}
```
This is, of course, not correct. The experiment employing the planner agent explicitly points out that the coercivity condition is incorrect.
gpt-6-sol then assumes that this is only a typo. In the `20260925_094853` experiment, where no planner agent is utilized,
the error is ignored and the correct definition is simply used. However, based on the available experiments on Cea's Lemma,
it is not possible to determine whether the proof was derived classically or whether it was part of the training data and was simply reproduced.
The `20260925_101906` and `20260925_101943` experiments indicate that the proof was part of the training data. Comparing the first
paragraphs of both results, we see that sentences are almost identical.

### Parabolic Estimator Deep Dive

An earlier version of `parabolic_estimator.tex` stated the Green's function representation lemma over
$W^1_2(0,T;H^1_0(\Omega))$ instead of the correct $W^1_2(0,T;H^1_0(\Omega),L^2(\Omega))$, which was wrong; this
was fixed before the `20260928_115447` and `20260928_120856` experiments. A separate, purely notational
inconsistency remained for those two experiments: the lemma used $W^{1,2}(0,T;H^1_0(\Omega),L^2(\Omega))$ while
the weak formulation earlier in the file used $W^1_2(0,T;V,H)$ for the same space, just with two different
superscript styles. This was made consistent for the `20260928_125327`, `20260928_130122`, `20260928_130604`,
and `20260928_130945` experiments; unlike the fix above, it does not change the mathematical content discussed
below.

`20260928_115447` and `20260928_120856` make the same mathematical mistake: they claim that the representation
lemma cannot be applied directly to $u-\widetilde R$, since the assumptions do not give its time derivative in
$L^2(0,T;H^1_0(\Omega))$ (or even just in $L^2(0,T;H^{-1}(\Omega))$), and consequently work around this with an unnecessary
approximation or "transposition" argument. This is incorrect. The reconstruction $\widetilde R$ is, by
construction, the continuous, piecewise affine-in-time interpolant of $R^0,\dots,R^M \in H^1_0(\Omega)$; on each
interval $I_j$ its time derivative is the constant $\delta_t R^j \in H^1_0(\Omega)$, so
$\widetilde R \in L^2(0,T;H^1_0(\Omega))$ with $\partial_t\widetilde R \in L^2(0,T;H^1_0(\Omega))$ trivially, and
hence, by the continuous embedding $H^1_0(\Omega)\hookrightarrow H^{-1}(\Omega)$, also
$\widetilde R \in W^1_2(0,T;H^1_0(\Omega),L^2(\Omega))$. Moreover, $u$ is already required to lie in
$W^1_2(0,T;H^1_0(\Omega),L^2(\Omega))$ by the problem's own weak formulation, so $u-\widetilde R$ lies in that
space too, by linearity, and the representation lemma applies directly without any approximation argument.

Notably, `20260928_120856` (no planner agent) is the only gpt-6-sol run so far to exhaust
`max_reviewer_iterations`, capping at 5 prover-reviewer iterations while constructing this flawed
justification — consistent with the reasoning being a genuine, effortful mistake rather than a shortcut.
Aside from this one mistake, both `20260928_115447` and `20260928_120856` are otherwise correct.

The `20260928_125327` and `20260928_130122` experiments, run against the fully corrected problem file, are
correct. The a posteriori error estimator's integral terms could be bounded more tightly, but that is a matter
of sharpness, not correctness. `20260928_115447`, `20260928_120856`, and `20260928_125327` all independently
point out that the problem statement's phrase "under standard assumptions on the function $f$" does not
actually specify sufficient regularity for $f$: the only precise hypothesis given, $f\in L^2(0,T;H^1_0(\Omega))$,
does not by itself guarantee finiteness of the weighted spatial maximum norms the maximum-norm estimate needs,
since the Green's-function weight $\phi_{1,\Gamma}(t)\sim 1/t$ is singular near $t=0$. This is a fair, recurring
criticism of the problem statement, not an error by the models.

The gpt-5.4-nano proofs are noticeably longer than gpt-6-sol's, but contain more issues. `20260928_130604`
(with planner) states a theorem asserting "there exists a constant $C$ depending only on the data," but the
proof never derives or bounds $C$ — it is invoked mid-proof via "using the properties of $c$, we obtain bounds
of the type... $\le C(\ldots)$" with no justification. The same theorem also defines $u_h$ as "any admissible
extension" of the discrete values, more general than the specific piecewise-affine extension the problem file
actually defines — yet the proof itself then explicitly narrows to "the piecewise-linear interpolation of
$u_h$," silently contradicting its own general hypothesis.

`20260928_130945` (without planner) contains no identified false step. It defines $w(t) = u(t) - R^M$ using the
fixed, time-independent final-time elliptic reconstruction, rather than $w(t) = u(t) - \widetilde R(t)$ as all
four gpt-6-sol proofs do. This choice is clever in one respect — since $R^M$ does not depend on $t$, $w$
trivially inherits $u$'s time regularity, sidestepping the $\widetilde R$-regularity question entirely — but it
introduces an extra term $\|R^0-R^M\|_{\infty,\Omega}$ (comparing the reconstructions at the *initial* and
*final* times, a global quantity unrelated to local discretization error) that the proof acknowledges and
claims will be "absorbed into the slab indicators below," yet the stated indicators never actually account for
it, and the term is silently dropped from the final estimate. This supports the suspicion that the resulting
estimator is not efficient, independently of whether any single step is technically false.

## Future Work

- Design an implementation pipeline that takes the theoretical results produced by the
  proof pipeline and verifies them numerically on suitable examples.
- Persist the PlannerReviewer/ProverReviewer feedback history to disk, so that
  runs which exhaust max_reviewer_iterations without approval can be debugged after
  the fact instead of only being visible as a raw iteration count.

## Acknowledgments

This project was developed with the assistance of Claude (Anthropic), an AI assistant,
which helped with coding, writing the documentation, and reviewing. The project idea,
the experiment design, the manual review of all generated proofs, and all final
decisions are my own.

## License

This project is licensed under the [MIT License](LICENSE).
