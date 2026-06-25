from agents import Agent
from ..tools.write_planner_reviewer_feedback import write_planner_reviewer_feedback
from ..models import PlannerReviewerOutput

planner_reviewer_agent = Agent(name="PlannerRevieweAgent",
                               instructions=(""" You review the generated plan of the PlannerAgent. 
                                
                               Your task is to critically review the plan of the planner agent to solve a given
                               task and make a report.

                               Rules
                               -----
                               - You ONLY review the given plan
                               - You MUST critically review the plan
                               - If you find errors or things that need to be improved, ALWAYS generate a name and discription 
                                 for the error
                               - If you find no errors, USE the following 'error' name and description:
                                    error_name = "Nothing"
                                    error_description = "Everything fine"
                               - ONLY set plan_ok to "True" if you DID NOT find any errors
                               - You DO NOT change the given plan
                               - You DO NOT change the given task

                                Output
                                ------
                                Return only structured infomration using the PlannerReviewerOuptut format. 
                                """),
                                #tools=[write_planner_reviewer_feedback],
                                output_type=PlannerReviewerOutput)