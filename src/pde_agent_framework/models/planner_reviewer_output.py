from pydantic import BaseModel, Field

class PlannerReviewerOutput(BaseModel):
    previous_plans: list[str] = Field(description="List that stores the current plan.") 
    error_name: list[str] = Field(description="List of error names. Error names must be short and clear names.")
    error_description: list[str] = Field(description="Description of the error. Should explain in a few words, what was wrong.")
    plan_ok: bool = Field(description="If the plan is okay, this attribute is set to True, otherwise to False.")
    #iterations: int = Field(description="Number of iterations.") 