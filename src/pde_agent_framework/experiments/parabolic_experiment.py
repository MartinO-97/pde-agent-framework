import asyncio
import os

from dotenv import load_dotenv

from ..schemas import ExperimentConfig, ExperimentOverview
from ..tools import run_proof_pipeline


async def main(user_input: str,
               output_directory: str,
               use_planner_agent: bool) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")

    if model_name is None:
        raise ValueError("'MODEL_NAME' is not defined.")

    experiment_config = ExperimentConfig(max_reviewer_iterations=5,
                                         model_name=model_name,
                                         use_planner_agent=use_planner_agent,
                                         problem_path=user_input,
                                         output_path=output_directory)

    experiment_overview = ExperimentOverview()
    experiment_overview.load_config(experiment_config)

    await run_proof_pipeline(experiment_config, experiment_overview)


async def run_both_configurations(user_input: str, output_directory: str) -> None:
    """Run the experiment once with the planner-reviewer structure and once without it."""
    print("Run with Planner Agent")
    await main(user_input, output_directory, use_planner_agent=True)
    
    print("")
    print("Without Planner Agent")
    await main(user_input, output_directory, use_planner_agent=False)


if __name__ == "__main__":

    asyncio.run(run_both_configurations("./problems/Parabolic_Estimator/parabolic_estimator.tex",
                                        "./results/Parabolic_Estimator/"))
