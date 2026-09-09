from agents import function_tool

@function_tool
def load_problem_file(file_path: str) -> str:

    """Load the file containing the mathematical problem statement.

    Args:
        file_path: Path to the problem description file.

    Returns:
        The raw text content of the problem statement.
    """

    with open(file_path, "r", encoding="utf-8") as f:

        problem_text = f.read()

    return problem_text