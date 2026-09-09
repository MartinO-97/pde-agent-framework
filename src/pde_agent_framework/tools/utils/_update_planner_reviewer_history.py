from ...schemas import PlannerReviewerOutput

def update_planner_reviewer_history(reviewer_history: PlannerReviewerOutput,
                                    reviewer_feedback: PlannerReviewerOutput) -> PlannerReviewerOutput:
    
    """Update the PlannerReviewer history by the newest feedback.

    Args:
        reviewer_history: The feedback history.
        reviewer_feedback: The current feedback of the PlannerReviewer.

    Returns:
        The updated PlannerReviewer feedback history.
    """

    #reviewer_history.previous_plans += reviewer_feedback.previous_plans
    #reviewer_history.error_name += reviewer_feedback.error_name
    reviewer_history.error_description += reviewer_feedback.error_description
    reviewer_history.plan_ok = reviewer_feedback.plan_ok

    return reviewer_history