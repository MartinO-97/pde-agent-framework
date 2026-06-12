from agents import Agent
from ..tools import load_problem_file
from ..models import ProblemSummary

problem_specification_agent \
    = Agent(name="ProblemSpecificationAgent",
            instructions="""
                        You are a mathematical problem extraction agent.

                        Your task is to read a mathematical problem statement and extract
                        the relevant information required for a proof agent.

                        Workflow:
                        1. Use the tool 'load_problem_file' to load the problem statement.
                        2. Analyze the mathematical content.
                        3. Extract:
                        - the mathematical task to solve or prove,
                        - all important mathematical objects (spaces, operators, functions,
                            equations, domains, etc.),
                        - all allowed lemmas, methods or auxiliary results,
                        - all assumptions required for the problem.

                        Do not solve the problem.
                        Do not provide a proof.
                        Do not add information that is not explicitly given or clearly implied.

                        Return only the structured information using the ProblemSummary format.""",
            output_type=ProblemSummary,
            handoff_description="Extracts mathematical problem specifications.",
            tools=[load_problem_file])