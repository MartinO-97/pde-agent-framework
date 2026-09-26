import argparse
import asyncio
import os

from dotenv import load_dotenv

from ..schemas import ExperimentConfig, ExperimentOverview
from ..tools import run_proof_pipeline


async def main(user_input: str,
               output_directory: str,
               use_planner_agent: bool) -> None:
    """Run a single Extract -> maybe Plan -> Prove -> Write experiment.

    Args:
        user_input: Path to the .tex file containing the problem description.
        output_directory: Path to the directory where the final proof shall be written.
        use_planner_agent: Whether the PlannerAgent-PlannerReviewerAgent loop shall be employed.

    Raises:
        ValueError: If the MODEL_NAME environment variable is not defined.
    """

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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for run_experiment.

    Returns:
        The parsed arguments, with problem_path, output_directory, and planner attributes.
    """
    parser = argparse.ArgumentParser(
        description="Run the Extract -> maybe Plan -> Prove -> Write proof pipeline on a single problem.")
    parser.add_argument("problem_path", help="Path to the .tex file containing the problem description.")
    parser.add_argument("output_directory", help="Path to the directory where the final proof shall be written.")
    parser.add_argument("--planner", action="store_true",
                        help="Employ the PlannerAgent-PlannerReviewerAgent loop. If omitted, planning is skipped.")
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    asyncio.run(main(args.problem_path, args.output_directory, args.planner))
