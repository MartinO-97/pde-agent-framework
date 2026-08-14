from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .experiment_config import ExperimentConfig


class ExperimentOverview(BaseModel):
    planner_reviewer_iterations: int = Field(default=0, description="Number of iterations of the Planner-PlannerReviewer Agents")
    prover_reviewer_iterations: int = Field(default=0, description="Number of iterations of the Prover-ProverReviewer Agents")
    max_reviewer_iterations: int = Field(default=0, description="Maximum number of iterations allowed for the reviewer loops")
    model_name: str = Field(default="", description="The model name used to generate the proof")
    use_planner_agent: bool = Field(default=False, description="Whether the PlannerAgent was employed")
    total_input_tokens: int = Field(default=0, description="Total number of input tokens consumed during the experiment")
    total_output_tokens: int = Field(default=0, description="Total number of output tokens consumed during the experiment")
    proof: str = Field(default="", description="The final proof produced by the WriterAgent")

    def update_token_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Add the given number of input and output tokens to the running total.

        Args:
            input_tokens: Number of input tokens to add.
            output_tokens: Number of output tokens to add.
        """
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def load_config(self, experiment_config: ExperimentConfig) -> None:
        """Extract the reviewer settings from the given ExperimentConfig.

        Copies the maximum number of reviewer iterations, the model name and
        whether the PlannerAgent shall be employed from the given config.

        Args:
            experiment_config: The configuration of the experiment.
        """
        self.max_reviewer_iterations = experiment_config.max_reviewer_iterations
        self.model_name = experiment_config.model_name
        self.use_planner_agent = experiment_config.use_planner_agent

    def update_reviewer_iterations(self, loop: Literal["planner", "prover"]) -> None:
        """Increment the iteration counter of the given reviewer loop.

        Args:
            loop: Which reviewer loop's iteration counter shall be incremented.

        Raises:
            ValueError: If loop is neither "planner" nor "prover".
        """
        if loop == "planner":
            self.planner_reviewer_iterations += 1
        elif loop == "prover":
            self.prover_reviewer_iterations += 1
        else:
            raise ValueError(f"loop must be 'planner' or 'prover', got '{loop}'.")

    def store_proof(self, proof: str) -> None:
        """Store the final proof produced by the WriterAgent.

        Args:
            proof: The final proof in LaTeX structure.
        """
        self.proof = proof

    def write_proof(self, output_directory: str) -> None:
        """Write the stored proof and the experiment parameters to disk.

        The proof is written to a .tex file, the remaining experiment
        parameters are written to a .json file.

        Args:
            output_directory: Path to the directory where the files shall be
                saved.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename_latex = f"{output_directory}{timestamp}.tex"
        filename_overview = f"{output_directory}{timestamp}_overview.json"

        with open(filename_latex, "w", encoding="utf-8") as f_latex, \
            open(filename_overview, "w", encoding="utf-8") as f_overview:

            f_latex.write(self.proof)
            f_overview.write(self.model_dump_json(indent=4, exclude={"proof"}))
