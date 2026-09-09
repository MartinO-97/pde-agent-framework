from functools import cache

from agents import Agent
from ..schemas import PlannerReviewerOutput


@cache
def create_planner_reviewer_agent() -> Agent:
    return Agent(name="PlannerReviewerAgent",
                 instructions=(""" You review the generated plan of the PlannerAgent.

                              Your task is to critically review the plan of the planner agent to solve a given
                              task and make a report.

                              Rules
                              -----
                              - You MUST critically review the plan
                              - You ONLY evaluate whether the plan is mathematically valid with respect to the provided ProblemSummary.
                              - You DO NOT modify the plan
                              - You DO NOT solve the problem.
                              - You DO NOT modify the given task
                              - If you find errors or things that need to be improved, ALWAYS generate a description for the error
                              - ONLY set plan_ok to "True" if you DID NOT find any errors

                               Output
                               ------
                               Return only structured information using the PlannerReviewerOutput format.
                               """),
                output_type=PlannerReviewerOutput)