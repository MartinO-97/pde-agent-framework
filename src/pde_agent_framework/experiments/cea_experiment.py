import asyncio
import os

from dotenv import load_dotenv
from ..agent_systems import problem_specification_agent, writer_agent, planner_agent, prover_agent, planner_reviewer_agent
from agents import Runner, RunConfig
from ..models import WriterInput, PlannerReviewerOutput, PlannerInput, ProblemSummary
from ..tools.write_proof import write_proof



async def main(user_input : str) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")    

    if model_name is None:
        raise ValueError("'MODEL' is not defined.")

    result_extractor = await Runner.run(starting_agent=problem_specification_agent,
                              input=f"Analyze the problem file: {user_input}.", 
                              run_config=RunConfig(model=model_name))
    
    if not isinstance(result_extractor.final_output, ProblemSummary):
        raise ValueError("Output type of problem_specification_agent is not of type ProblemSummary.")

    planner_reviewer_result = PlannerReviewerOutput(previous_plans=[], error_name=[], error_description=[], plan_ok=False, 
                                                    iterations=0)
    planner_input = PlannerInput(problem_summary= result_extractor.final_output)

    while not planner_reviewer_result.plan_ok and planner_reviewer_result.iterations <=5:

        result_planner = await Runner.run(starting_agent=planner_agent,
                                input=f"Plan a proof: {planner_input}.", 
                                run_config=RunConfig(model=model_name))
        
        planner_reviewer_result = await Runner.run(starting_agent=planner_reviewer_agent,
                                                   input=f"Review {result_planner.final_output} and update {planner_reviewer_result}",
                                                   run_config=RunConfig(model=model_name))
        
        planner_reviewer_result = planner_reviewer_result.final_output
        
        if not isinstance(planner_reviewer_result, PlannerReviewerOutput):
            raise ValueError("planner_reviewer_result is not of type PlannerReviewerOutput!") 
        
        planner_input = PlannerInput(problem_summary=result_extractor.final_output, planner_reviewer_feedback=planner_reviewer_result)
        
        
    result_prover = await Runner.run(starting_agent=prover_agent,
                                     input=f"Generate a complete proof: {result_planner.final_output}",
                                     run_config=RunConfig(model=model_name))

    writer_input = WriterInput(proof=result_prover.final_output, output_directory="./results/Ceas_Lemma_Proof/ceas_lemma_proof")

    latex_proof = await Runner.run(starting_agent=writer_agent,
                                   input=f"Rewrite the following proof in Latex: {writer_input}")

    write_proof(latex_proof.final_output, planner_reviewer_result, "./results/Ceas_Lemma_Proof/ceas_lemma_proof")

if __name__ == "__main__":

    asyncio.run(main("./problems/Ceas_Lemma_Proof/ceas_lemma_proof.tex"))