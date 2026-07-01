from ..models import PlannerReviewerOutput

def update_planner_reviewer_history(reviewer_history: PlannerReviewerOutput,
                                    reviewer_feedback: PlannerReviewerOutput) -> PlannerReviewerOutput:
    
    r""" Update the PlannerReviewer history by the newest feedback.
    
    Parameters
    ----------
    reviewer_history: PlannerReviewerOutput
        The feedback history.

    reviewer_feedback: PlannerReviewerOutput
        The current feedback of the PlannerReviewer.

    Returns
    -------
    reviewer_history: PlannerReviewerOutput
        The updated PlannerReviewer feedback history.
    """

    #reviewer_history.previous_plans += reviewer_feedback.previous_plans
    #reviewer_history.error_name += reviewer_feedback.error_name
    reviewer_history.error_description += reviewer_feedback.error_description
    reviewer_history.plan_ok = reviewer_feedback.plan_ok

    return reviewer_history