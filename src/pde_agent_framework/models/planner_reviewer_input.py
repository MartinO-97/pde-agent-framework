from pydantic import BaseModel
from planner_result import PlannerResult
from planner_reviewer_output import PlannerReviewerOutput

class PlannerReviewerInput(BaseModel):
    plan: PlannerResult
    report_history: PlannerReviewerOutput