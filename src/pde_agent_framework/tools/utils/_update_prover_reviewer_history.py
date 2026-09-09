from ...schemas import ProverReviewerOutput

def update_prover_reviewer_history(reviewer_history: ProverReviewerOutput,
                                   reviewer_feedback: ProverReviewerOutput) -> ProverReviewerOutput:
    
    """Update the ProverReviewer history by the newest feedback.

    Args:
        reviewer_history: The feedback history.
        reviewer_feedback: The current feedback of the ProverReviewer.

    Returns:
        The updated ProverReviewer feedback history.
    """

    #reviewer_history.previous_proofs += reviewer_feedback.previous_proofs
    #reviewer_history.error_name += reviewer_feedback.error_name
    reviewer_history.error_description += reviewer_feedback.error_description
    reviewer_history.proof_ok = reviewer_feedback.proof_ok

    return reviewer_history