from pydantic import BaseModel, Field

class ExperimentOverview(BaseModel):
    planner_reviewer_iterations: int = Field(description="Number of iterations of the Planner-PlannerReviewer Agents")
    prover_reviewer_iterations: int = Field(description="Number of iterations of the Prover-ProverReviewer Agents")
    model_name: str = Field(description="The model name used to gnerate the proof")