from functools import cache

from agents import Agent
from .problem_specification_agent import create_problem_specification_agent
from .planner_agent import create_planner_agent


@cache
def create_manager_agent() -> Agent:
    return Agent(name="ManagerAgent",
                instructions="""You are a workflow manager for mathematical proof tasks.

                                Your task is to coordinate the available specialist agents.

                                You MUST execute the workflow in strict order:
                                1. Call ProblemSpecificationAgent.
                                2. WAIT for its output.
                                3. Call PlanerAgent with that output.
                                4. Return ONLY the PlanerAgent output.

                                Rules:
                                It is not allowed to skip any step.
                                It is not allowed to return early.
                                You do not analyze the mathematical problem yourself.
                                You do not solve the problem.
                                You do not create proofs.
                                You only delegate tasks and pass results between agents.

                                Always use the available specialist agents when appropriate.
                                """,
                handoffs=[create_problem_specification_agent(), create_planner_agent()])