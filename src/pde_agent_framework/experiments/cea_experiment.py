import asyncio
import os

from dotenv import load_dotenv
from ..agent_systems import manager_agent
from openai import OpenAI
from agents import Agent, Runner, RunConfig



async def main(user_input : str) -> None:

    load_dotenv()

    model_name = os.getenv("MODEL_NAME")    

    if model_name is None:
        raise ValueError("'MODEL' is not defined.")

    result = await Runner.run(starting_agent=manager_agent,
                              input=f"Analyze the problem file: {user_input}.", 
                              run_config=RunConfig(model=model_name))
    
    print(result.final_output)


if __name__ == "__main__":

    asyncio.run(main("./problems/Ceas_Lemma_Proof/ceas_lemma_proof.tex"))