import asyncio
import os

from dotenv import load_dotenv
from ..agent_systems import problem_specification_agent, writer_agent, planner_agent, prover_agent, \
    planner_reviewer_agent, prover_reviewer_agent
from agents import Runner, RunConfig
from ..models import WriterInput, PlannerReviewerOutput, PlannerInput, ProblemSummary, ProverReviewerOutput, \
    ProverInput, PlannerResult, PlannerReviewerInput, ProverReviewerInput, ModelName
from ..tools import write_proof, write_failure_output, update_planner_reviewer_history, \
    update_prover_reviewer_history



async def main(user_input : str, 
               output_directory: str) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")    
    model_name_class = ModelName(model_name=model_name)

    if model_name is None:
        raise ValueError("'MODEL' is not defined.")

    #----------------------------------------------------------------------------------------------------
    # INFORMATION EXTRACTING
    #----------------------------------------------------------------------------------------------------
    print("Start extracting process")

    result_extractor = await Runner.run(starting_agent=problem_specification_agent,
                              input=f"Analyze the problem file: {user_input}.", 
                              run_config=RunConfig(model=model_name))
    
    result_extractor = result_extractor.final_output

    if not isinstance(result_extractor, ProblemSummary):
        raise ValueError("Output type of problem_specification_agent is not of type ProblemSummary.")

    print("Finished extracting process")
    #----------------------------------------------------------------------------------------------------
    # PLANNING
    #----------------------------------------------------------------------------------------------------
    print("Start planning process")
    planner_iterations = 0
    planner_reviewer_history = PlannerReviewerOutput(previous_plans=[], error_name=[], 
                                                     error_description=[], plan_ok=False)
    
    planner_input = PlannerInput(problem_summary = result_extractor)

    while not planner_reviewer_history.plan_ok and planner_iterations <5:

        planner_iterations += 1

        result_planner = await Runner.run(starting_agent=planner_agent,
                                input=f"Plan a proof: {planner_input}.", 
                                run_config=RunConfig(model=model_name))
        
        result_planner = result_planner.final_output

        planner_reviewer_input = PlannerReviewerInput(plan= result_planner,
                                                      problem_summary=result_extractor)

        planner_reviewer_result = await Runner.run(starting_agent=planner_reviewer_agent,
                                                   input=f"Review the plan given in {planner_reviewer_input}.",
                                                   run_config=RunConfig(model=model_name))

        planner_reviewer_result = planner_reviewer_result.final_output

        if not isinstance(planner_reviewer_result, PlannerReviewerOutput):
            raise ValueError("planner_reviewer_result is not of type PlannerReviewerOutput!") 
        
        planner_reviewer_history = \
            update_planner_reviewer_history(planner_reviewer_history, planner_reviewer_result)

        planner_input = PlannerInput(problem_summary=result_extractor, 
                                     planner_reviewer_feedback=planner_reviewer_history)

    if planner_iterations >= 5: 
        print("Planning process failed -> Abort")
        prover_reviewer_result = ProverReviewerOutput(previous_proofs=[], error_name=[], error_description=[], 
                                                  proof_ok=False)
        write_proof(write_failure_output("planning"), planner_reviewer_result,
                    prover_reviewer_result, output_directory)
        return
    
    if not isinstance(result_planner, PlannerResult):
        raise ValueError("result_planner is not of type PlannerResult")

    print(f"Finished planning process. Number of iterations: {planner_iterations}")
    #----------------------------------------------------------------------------------------------------
    # PROVING
    #----------------------------------------------------------------------------------------------------
    print("Start proving process")

    prover_iterations = 0

    prover_reviewer_history = ProverReviewerOutput(previous_proofs=[], error_name=[], error_description=[], 
                                                  proof_ok=False)
    
    prover_input = ProverInput(plan=result_planner)

    while not prover_reviewer_history.proof_ok and prover_iterations <5:

        prover_iterations += 1

        result_prover = await Runner.run(starting_agent=prover_agent,
                                        input=f"Generate a complete proof: {prover_input}",
                                        run_config=RunConfig(model=model_name))
        
        result_prover = result_prover.final_output

        prover_reviewer_input = ProverReviewerInput(proof=result_prover, 
                                                    problem_summary=result_extractor)

        prover_reviewer_result = await Runner.run(starting_agent=prover_reviewer_agent,
                                            input=f"Review {prover_reviewer_input}",
                                            run_config=RunConfig(model=model_name))
        
        prover_reviewer_result = prover_reviewer_result.final_output
        
        if not isinstance(prover_reviewer_result, ProverReviewerOutput):
            raise ValueError("planner_reviewer_result is not of type ProverReviewerOutput!") 
        
        prover_reviewer_history = \
            update_prover_reviewer_history(prover_reviewer_history, prover_reviewer_result)

    if prover_iterations >= 5: 
        print("Proving process failed -> Abort")
        write_proof(write_failure_output("proving"), planner_reviewer_result,
                    prover_reviewer_result, output_directory)
        return

    print(f"Finished proving process. Number of iterations: {prover_iterations}")
    #----------------------------------------------------------------------------------------------------
    # WRITING
    #----------------------------------------------------------------------------------------------------
    print("Start writing process")
    writer_input = WriterInput(proof=result_prover)

    latex_proof = await Runner.run(starting_agent=writer_agent,
                                   input=f"Rewrite the following proof in Latex: {writer_input}")

    write_proof(latex_proof.final_output, planner_reviewer_result, prover_reviewer_result,
                model_name, output_directory)

    print("Finished writing process")

if __name__ == "__main__":

    asyncio.run(main("./problems/Parabolic_Estimator/parabolic_estimator.tex",
                     "./results/Parabolic_Estimator/"))