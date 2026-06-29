from datetime import datetime
from agents import function_tool
from ..models import PlannerReviewerOutput, ProverReviewerOutput, \
                     ModelName

#@function_tool
def write_proof(latex_proof: str,
                planner_reviewer_feedback: PlannerReviewerOutput,
                prover_reviewer_feedback: ProverReviewerOutput,
                model_name_class: ModelName,
                output_directory: str) -> None:

    r""" Write a prove in Latex structure. 
    
    Parameters
    ----------
    latex_proof: str
        A generated proof in Latex structure

    planner_reviewer_feedback: PlannerReviewerOutput
        The feedback(s) of the PlannerReviewer

    prover_reviewer_feedback: ProverReviewerOutput
        The feedback(s) of the ProverReviewer

    output_director : str
        Path to file where the .tex shall be saved.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename_latex = f"{output_directory}"+f"{timestamp}.tex"
    filename_planner_reviewer = f"{output_directory}"+f"{timestamp}_planner_feedback.json"
    filename_prover_reviewer = f"{output_directory}"+f"{timestamp}_prover_feedback.json"
    filename_model_name = f"{output_directory}"+f"{timestamp}_model_used.json"

    with open(filename_latex, "w", encoding="utf-8") as f_latex, \
        open(filename_planner_reviewer, "w") as f_planner_json, \
        open(filename_prover_reviewer, "w") as f_prover_json, \
        open(filename_model_name, "w") as f_model_json:

        f_planner_json.write(planner_reviewer_feedback.model_dump_json(indent=4))
        f_prover_json.write(prover_reviewer_feedback.model_dump_json(indent=4))
        f_model_json.write(model_name_class.model_dump_json(indent=4))
        f_latex.write(latex_proof)