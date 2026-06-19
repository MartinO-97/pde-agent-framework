from pydantic import BaseModel

class PlannerReviewerOutput(BaseModel):
    previous_plans: list[str] 
    error_name: list[str] 
    error_discription: list[str] 
    plan_ok: bool
    iterations: int 