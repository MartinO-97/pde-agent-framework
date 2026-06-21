from pydantic import BaseModel, Field
from .problem_summary import ProblemSummary
from. planner_reviewer_output import PlannerReviewerOutput

class PlannerInput(BaseModel):
    problem_summary: ProblemSummary = Field(description=" Summary of the problem using the ProblemSummary class. ")
    planner_reviewer_feedback: PlannerReviewerOutput | None = Field(default= None, 
                                                                    description=
                                                                    ("""The review of the planner_reviewer agent. The PlannerReviewerOutput class
                                                                    is used to save the feedbacks in a planner-planner_reviewer loop. If the planner_agent is 
                                                                    called the first time, this attribute is set to None. """))