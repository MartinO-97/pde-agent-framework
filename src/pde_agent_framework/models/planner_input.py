from pydantic import BaseModel
from .problem_summary import ProblemSummary
from. planner_reviewer_output import PlannerReviewerOutput

class PlannerInput(BaseModel):
    problem_summary: ProblemSummary
    planner_reviewer_feedback: PlannerReviewerOutput | None = None