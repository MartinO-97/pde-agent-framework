from ..models import PlannerReviewerOutput
from agents import function_tool

@function_tool
def write_planner_reviewer_feedback(error_log: PlannerReviewerOutput,
                                    error_name: str, 
                                    error_description: str,
                                    reviewed_plan: str,
                                    plan_ok: bool) -> PlannerReviewerOutput:
    
    r""" Tool to safe planner_reviewer feedback.

    Parameters
    ----------
    error_log: PlannerReviewerOutput
        The current planner_reviewer output object

    error_name: str
        Name for detected error
    
    error_description: str
        Description of detected error

    reviewed_plan
        Plan reviewed by the planner_reviewer

    plan_ok: bool
        Was the reviewed plan ok? -> Yes == "True", No== "False"

    Returns
    -------
    :PlannerReviewerOutput
        Updated planner_reviewer ouput object
    """

    error_log.error_name += [error_name]
    error_log.error_description += [error_description]
    error_log.plan_ok = plan_ok
    error_log.previous_plans += [reviewed_plan]
    error_log.iterations += 1

    return error_log