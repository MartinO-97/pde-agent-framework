from datetime import datetime
from agents import function_tool
from agents import function_tool

@function_tool
def write_proof(latex_proof: str,
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

    filename = f"{output_directory}_{timestamp}.tex"

    with open(filename, "w", encoding="utf-8") as f:

        f.write(latex_proof)