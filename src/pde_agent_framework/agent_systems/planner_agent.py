from agents import Agent
from ..models import PlannerResult
#from ..agent_systems import prover_agent

planner_agent = Agent(name="PlanerAgent",
                     instructions=""" You are a planner of a mathematical proof. 
                                      
                                      Your task is to design a structured proof strategy for a given mathematical problem.

                                      Input structure:
                                      1. task: the mathematical task to solve or prove,
                                      2. mathematical_objects: all important mathematical objects (spaces, operators, functions,
                                        equations, domains, etc.),
                                      3. allowed_lemmas_and_theorems: All allowed lemmas, theorems methods or auxiliary results. 
                                      4. assumptions: all assumptions required to solve the problem.
                                      5. raw_input: the raw .tex file content
                                      
                                      Output:
                                      Provide a numbered sequence of proof steps and the task from the input.
                                      
                                      Important rules:
                                      - Do not write a full proof.
                                      - Do not produce LaTeX.
                                      - Do not justify steps in detail.
                                      - Do not change the task.
                                      - Only output a structured proof outline.
                                      - Each step should describe a mathematical idea or argument, not computations.
                                      - If allowed_lemmas_and_theorems is non-empty: Use only these results unless absolutely necessary.
                                      - If allowed_lemmas_and_theorems is an empty list or None: 
                                            -> You are in OPEN MATHEMATICAL MODE.
                                            -> You may select appropriate lemmas and theorems from general mathematical knowledge.

                                      In OPEN MODE:
                                      - Clearly state which classical results you are using.
                                      - Do not invent new theorems.
                                      - Prefer well-known results from analysis, PDE theory, or functional analysis.
                                      
                                      Output structure:
                                      - plan: Your provided plan
                                      - taskt: The task from the input

                                      Return only the structured information using the PlannerResult format.
                                  """,
                     handoff_description="Provides the structure of the proof of the mathematical problem",
                     #handoffs=[prover_agent],
                     output_type=PlannerResult)