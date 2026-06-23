from datetime import datetime
from agents import function_tool
from ..models import PlannerReviewerOutput, ProverReviewerOutput

#@function_tool
def write_proof(latex_proof: str,
                planner_reviewer_feedback: PlannerReviewerOutput,
                prover_reviewer_feedback: ProverReviewerOutput,
                output_directory: str) -> None:

    r""" Write a prove in Latex structure. 
    
    Parameters
    ----------
    latex_proof: str
        A generated proof in Latex structure

    output_director : str
        Path to file where the .tex shall be saved.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename_latex = f"{output_directory}_{timestamp}.tex"
    filename_planner_reviewer = f"{output_directory}_{timestamp}_planner_feedback.json"
    filename_prover_reviewer = f"{output_directory}_{timestamp}_prover_feedback.json"

    with open(filename_latex, "w", encoding="utf-8") as f_latex, \
        open(filename_planner_reviewer, "w") as f_planner_json, \
        open(filename_prover_reviewer, "w") as f_prover_json:

        f_planner_json.write(planner_reviewer_feedback.model_dump_json(indent=4))
        f_prover_json.write(prover_reviewer_feedback.model_dump_json(indent=4))
        f_latex.write(latex_proof)