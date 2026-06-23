from agents import Agent
from ..tools import write_prover_reviewer_feedback
from ..models import ProverReviewerOutput

prover_reviewer_agent = Agent(name="ProverReviewer", 
                              instructions=(""" You review the generated plan of the planner_agent. 
                                
                               Your task is to critically review the proof, that proves a
                                mathematical claim or a problem, of the ProverAgent make a report.

                               Rules
                               -----
                               - You ONLY review the given proof
                               - You MUST critically review the proof
                               - If you find errors or things that need to be improved, ALWAYS generate a name and discription 
                                 for the error
                               - If you find no errors, USE the following 'error' name and description:
                                    error_name = "Nothing"
                                    error_description = "Everything fine"
                               - ONLY set proof_ok to "True" if you DID NOT find any errors
                               - To save your report ALWAYS employ the given tool
                               - You ALWAYS update the given ProverReviewerOutput object by using the given tool
                               - You only return the updated ProverReviewerOutput object that was given to you
                               - You DO NOT change the given proof
                               - You DO NOT change the given task

                                Output
                                ------
                                Return only structured infomration using the ProverReviewerOuptut format. 
                                """),
                                tools=[write_prover_reviewer_feedback],
                                output_type=ProverReviewerOutput)