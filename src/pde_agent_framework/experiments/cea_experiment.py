import asyncio
import os

from dotenv import load_dotenv
from ..agent_systems import problem_specification_agent, writer_agent, planner_agent, prover_agent
from agents import Agent, Runner, RunConfig
from ..models import WriterInput



async def main(user_input : str) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")    

    if model_name is None:
        raise ValueError("'MODEL' is not defined.")

    result_extractor = await Runner.run(starting_agent=problem_specification_agent,
                              input=f"Analyze the problem file: {user_input}.", 
                              run_config=RunConfig(model=model_name))
    
    result_planner = await Runner.run(starting_agent=planner_agent,
                              input=f"Plan a proof: {result_extractor.final_output}.", 
                              run_config=RunConfig(model=model_name))
    
    result_prover = await Runner.run(starting_agent=prover_agent,
                                     input=f"Generate a complete proof: {result_planner.final_output}",
                                     run_config=RunConfig(model=model_name))

    writer_input = WriterInput(proof=result_prover.final_output, output_directory="./results/Ceas_Lemma_Proof/ceas_lemma_proof")

    await Runner.run(starting_agent=writer_agent,
                     input=f"Rewrite the following proof in Latex: {writer_input}")


if __name__ == "__main__":

    asyncio.run(main("./problems/Ceas_Lemma_Proof/ceas_lemma_proof.tex"))