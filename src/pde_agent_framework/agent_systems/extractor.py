from agents import Agent

from models import ProblemSummary

problem_specification_agent \
    = Agent(name="ProblemSpecificator",
            instructions="",
            output_type=ProblemSummary,
            handoff_description="")