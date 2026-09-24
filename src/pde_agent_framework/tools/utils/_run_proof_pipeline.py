from agents import Runner, RunConfig

from ...agent_systems import (create_planner_agent, create_planner_reviewer_agent,
                              create_problem_specification_agent, create_prover_agent,
                              create_prover_reviewer_agent, create_writer_agent)
from ...schemas import ExperimentConfig, ExperimentOverview, PlannerResult, ProblemSummary, ProverResult, WriterInput
from ._agent_reviewer_loop import agent_reviewer_loop


async def run_proof_pipeline(
        experiment_config: ExperimentConfig, 
        experiment_overview: ExperimentOverview) -> None:
    
    """Run the full Extract -> maybe Plan -> Prove -> Write workflow for one experiment.

    Requires experiment_overview.load_config(experiment_config) to have already
    been called by the caller.

    Args:
        experiment_config: Configuration of the experiment to run.
        experiment_overview: Overview instance that is populated with the results of
            the experiment as it progresses and finally written to disk.

    Raises:
        ValueError: If experiment_overview.load_config(experiment_config) was not
            called before run_proof_pipeline.
    """
    if experiment_overview.model_name != experiment_config.model_name:
        raise ValueError("experiment_overview.load_config(experiment_config) must be called "
                         "before run_proof_pipeline.")

    print("Start extracting process")
    result_extractor = await Runner.run(starting_agent=create_problem_specification_agent(),
                                        input=f"Analyze the problem file: {experiment_config.problem_path}.",
                                        run_config=RunConfig(model=experiment_config.model_name))
    problem_summary = result_extractor.final_output

    if not isinstance(problem_summary, ProblemSummary):
        raise ValueError("Output type of problem_specification_agent is not of type ProblemSummary.")
    print("Finished extracting process")

    if experiment_config.use_planner_agent:
        print("Start planning process")
        result_planner, _ = await agent_reviewer_loop(main_agent=create_planner_agent(),
                                                       reviewer_agent=create_planner_reviewer_agent(),
                                                       problem_summary=problem_summary,
                                                       plan=None,
                                                       experiment_config=experiment_config,
                                                       experiment_overview=experiment_overview,
                                                       loop_name="planner")

        if not isinstance(result_planner, PlannerResult):
            raise ValueError("result_planner is not of type PlannerResult")
        print(f"Finished planning process. Number of iterations: {experiment_overview.planner_reviewer_iterations}")
    else:
        result_planner = PlannerResult(plan="")

    print("Start proving process")
    result_prover, _ = await agent_reviewer_loop(main_agent=create_prover_agent(),
                                                  reviewer_agent=create_prover_reviewer_agent(),
                                                  problem_summary=problem_summary,
                                                  plan=result_planner,
                                                  experiment_config=experiment_config,
                                                  experiment_overview=experiment_overview,
                                                  loop_name="prover")

    if not isinstance(result_prover, ProverResult):
        raise ValueError("result_prover is not of type ProverResult")
    print(f"Finished proving process. Number of iterations: {experiment_overview.prover_reviewer_iterations}")

    print("Start writing process")
    writer_input = WriterInput(proof=result_prover)
    latex_proof = await Runner.run(starting_agent=create_writer_agent(),
                                   input=f"Rewrite the following proof in Latex: {writer_input}")

    experiment_overview.store_proof(latex_proof.final_output)
    experiment_overview.write_proof(experiment_config.output_path)
    print("Finished writing process")
