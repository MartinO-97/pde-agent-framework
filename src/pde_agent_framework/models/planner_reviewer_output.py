from pydantic import BaseModel

class PlannerReviewerOutput(BaseModel):
    previous_plans: list[str] 
    error_name: list[str] 
    error_description: list[str] 
    plan_ok: bool
    iterations: int 