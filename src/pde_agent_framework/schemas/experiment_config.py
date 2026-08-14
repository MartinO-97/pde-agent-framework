from pydantic import BaseModel, Field

class ExperimentConfig(BaseModel):
    max_reviewer_iterations: int = Field(description="Maximum number of iterations for the planner/prover reviewer loops.")
    model_name: str = Field(description="The model name used to run the experiment.")
    use_planner_agent: bool = Field(description="Whether the PlannerAgent shall be employed.")
    problem_path: str = Field(description="Path to the .tex file containing the problem description.")
    output_path: str = Field(description="Path to the directory where the final proof shall be written.")
