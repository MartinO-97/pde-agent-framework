from ..models import ProverReviewerOutput
from agents import function_tool

@function_tool
def write_prover_reviewer_feedback(error_log: ProverReviewerOutput,
                                    error_name: str, 
                                    error_description: str,
                                    reviewed_proof: str,
                                    proof_ok: bool) -> ProverReviewerOutput:
    
    r""" Tool to safe planner_reviewer feedback.

    Parameters
    ----------
    error_log: ProverReviewerOutput
        The current planner_reviewer output object
        
    error_name: str
        Name for detected error
    
    error_description: str
        Description of detected error

    reviewed_proof: str
        Proof reviewed by the ProverReviewerAgent

    plan_ok: bool
        Was the reviewed proof ok? -> Yes == "True", No== "False"

    Returns
    -------
    :ProverReviewerOutput
        Updated planner_reviewer ouput object
    """

    error_log.error_name += [error_name]
    error_log.error_description += [error_description]
    error_log.proof_ok = proof_ok
    error_log.previous_proofs += [reviewed_proof]
    #error_log.iterations += 1

    return error_log