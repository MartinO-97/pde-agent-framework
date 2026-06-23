import asyncio
import os

from dotenv import load_dotenv
from ..agent_systems import problem_specification_agent, writer_agent, planner_agent, prover_agent, planner_reviewer_agent, prover_reviewer_agent
from agents import Runner, RunConfig
from ..models import WriterInput, PlannerReviewerOutput, PlannerInput, ProblemSummary, ProverReviewerOutput, ProverReviewerInput, ProverInput, \
                     PlannerResult
from ..tools.write_proof import write_proof



async def main(user_input : str) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")    

    if model_name is None:
        raise ValueError("'MODEL' is not defined.")

    #----------------------------------------------------------------------------------------------------
    # INFORMATION EXTRACTING
    #----------------------------------------------------------------------------------------------------

    result_extractor = await Runner.run(starting_agent=problem_specification_agent,
                              input=f"Analyze the problem file: {user_input}.", 
                              run_config=RunConfig(model=model_name))
    
    result_extractor = result_extractor.final_output

    if not isinstance(result_extractor, ProblemSummary):
        raise ValueError("Output type of problem_specification_agent is not of type ProblemSummary.")

    #----------------------------------------------------------------------------------------------------
    # PLANNING
    #----------------------------------------------------------------------------------------------------
    planner_reviewer_result = PlannerReviewerOutput(previous_plans=[], error_name=[], error_description=[], plan_ok=False, 
                                                    iterations=0)
    
    planner_input = PlannerInput(problem_summary = result_extractor)

    while not planner_reviewer_result.plan_ok and planner_reviewer_result.iterations <=5:

        result_planner = await Runner.run(starting_agent=planner_agent,
                                input=f"Plan a proof: {planner_input}.", 
                                run_config=RunConfig(model=model_name))
        
        result_planner = result_planner.final_output

        planner_reviewer_result = await Runner.run(starting_agent=planner_reviewer_agent,
                                                   input=f"Review {result_planner} and update {planner_reviewer_result}",
                                                   run_config=RunConfig(model=model_name))
        
        planner_reviewer_result = planner_reviewer_result.final_output
        
        if not isinstance(planner_reviewer_result, PlannerReviewerOutput):
            raise ValueError("planner_reviewer_result is not of type PlannerReviewerOutput!") 
        
        planner_input = PlannerInput(problem_summary=result_extractor, planner_reviewer_feedback=planner_reviewer_result)

    if not isinstance(result_planner, PlannerResult):
        raise ValueError("result_planner is not of type PlannerResult")

    #----------------------------------------------------------------------------------------------------
    # PROVING
    #----------------------------------------------------------------------------------------------------
    prover_reviewer_result = ProverReviewerOutput(previous_proofs=[], error_name=[], error_description=[], 
                                                  proof_ok=False, iterations=0)
    
    prover_input = ProverInput(plan=result_planner)

    while not prover_reviewer_result.proof_ok and prover_reviewer_result.iterations <=5:

        result_prover = await Runner.run(starting_agent=prover_agent,
                                        input=f"Generate a complete proof: {prover_input}",
                                        run_config=RunConfig(model=model_name))
        
        result_prover = result_prover.final_output

        prover_reviewer_result = await Runner.run(starting_agent=prover_reviewer_agent,
                                            input=f"Review {result_prover} and update {prover_reviewer_result}",
                                            run_config=RunConfig(model=model_name))
        
        prover_reviewer_result = prover_reviewer_result.final_output
        
        if not isinstance(prover_reviewer_result, ProverReviewerOutput):
            raise ValueError("planner_reviewer_result is not of type ProverReviewerOutput!") 

    #----------------------------------------------------------------------------------------------------
    # WRITING
    #----------------------------------------------------------------------------------------------------
    writer_input = WriterInput(proof=result_prover.final_output, output_directory="./results/Ceas_Lemma_Proof/ceas_lemma_proof")

    latex_proof = await Runner.run(starting_agent=writer_agent,
                                   input=f"Rewrite the following proof in Latex: {writer_input}")

    write_proof(latex_proof.final_output, planner_reviewer_result, "./results/Ceas_Lemma_Proof/ceas_lemma_proof")

if __name__ == "__main__":

    asyncio.run(main("./problems/Ceas_Lemma_Proof/ceas_lemma_proof.tex"))