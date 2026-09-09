from ...schemas import PlannerReviewerOutput
from agents import function_tool

@function_tool
def write_planner_reviewer_feedback(error_log: PlannerReviewerOutput,
                                    error_name: str, 
                                    error_description: str,
                                    reviewed_plan: str,
                                    plan_ok: bool) -> PlannerReviewerOutput:
    
    """Save PlannerReviewer feedback.

    Args:
        error_log: The current planner_reviewer output object.
        error_name: Name for the detected error.
        error_description: Description of the detected error.
        reviewed_plan: Plan reviewed by the planner_reviewer.
        plan_ok: Was the reviewed plan ok? -> Yes == "True", No == "False".

    Returns:
        Updated planner_reviewer output object.
    """
    error_log.error_name += [error_name]
    error_log.error_description += [error_description]
    error_log.plan_ok = plan_ok
    error_log.previous_plans += [reviewed_plan]
    #error_log.iterations += 1

    return error_log