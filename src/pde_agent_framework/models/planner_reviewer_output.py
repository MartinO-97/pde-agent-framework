from pydantic import BaseModel

class PlannerReviewerOutput(BaseModel):
    previous_plans: list[str] = []
    error_name: list[str] = []
    error_message: list[str]  = []
    plan_ok: bool
    iterations: int = 0