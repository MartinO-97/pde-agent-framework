from ...schemas import ProverReviewerOutput
from agents import function_tool

@function_tool
def write_prover_reviewer_feedback(error_log: ProverReviewerOutput,
                                    error_name: str, 
                                    error_description: str,
                                    reviewed_proof: str,
                                    proof_ok: bool) -> ProverReviewerOutput:
    
    """Save ProverReviewer feedback.

    Args:
        error_log: The current prover_reviewer output object.
        error_name: Name for the detected error.
        error_description: Description of the detected error.
        reviewed_proof: Proof reviewed by the ProverReviewerAgent.
        proof_ok: Was the reviewed proof ok? -> Yes == "True", No == "False".

    Returns:
        Updated prover_reviewer output object.
    """

    error_log.error_name += [error_name]
    error_log.error_description += [error_description]
    error_log.proof_ok = proof_ok
    error_log.previous_proofs += [reviewed_proof]
    #error_log.iterations += 1

    return error_log