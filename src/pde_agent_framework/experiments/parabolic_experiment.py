import asyncio
import os

from dotenv import load_dotenv

from ..schemas import ExperimentConfig, ExperimentOverview
from ..tools import run_proof_pipeline


async def main(user_input: str,
               output_directory: str) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")

    if model_name is None:
        raise ValueError("'MODEL_NAME' is not defined.")

    experiment_config = ExperimentConfig(max_reviewer_iterations=5,
                                         model_name=model_name,
                                         use_planner_agent=True,
                                         problem_path=user_input,
                                         output_path=output_directory)

    experiment_overview = ExperimentOverview()
    experiment_overview.load_config(experiment_config)

    await run_proof_pipeline(experiment_config, experiment_overview)


if __name__ == "__main__":

    asyncio.run(main("./problems/Parabolic_Estimator/parabolic_estimator.tex",
                     "./results/Parabolic_Estimator/"))
