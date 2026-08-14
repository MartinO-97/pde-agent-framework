from ..schemas import ProverReviewerOutput

def update_prover_reviewer_history(reviewer_history: ProverReviewerOutput,
                                   reviewer_feedback: ProverReviewerOutput) -> ProverReviewerOutput:
    
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

    #reviewer_history.previous_proofs += reviewer_feedback.previous_proofs
    #reviewer_history.error_name += reviewer_feedback.error_name
    reviewer_history.error_description += reviewer_feedback.error_description
    reviewer_history.proof_ok = reviewer_feedback.proof_ok

    return reviewer_history