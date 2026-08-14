from pydantic import BaseModel, Field

r""" Class that defines the output scheme of the extractor agent """

class ProblemSummary(BaseModel):
    task: str = Field(description="The mathematical problem to solve -> Only a short sentence describing the problem.")
    mathematical_objects: list[str] = Field(description=
                                            ("""List of mathematical objects such as spaces, domains and 
                                            functions provided by the .tex file."""))
    allowed_lemmas_and_theorems: list[str] = Field(description=(
                                                   """List of allowed lemmas, results and theorems. 
                                                   Examples: ["Hoelder inequality", "Young's inequality"]""")) 
    assumptions: list[str] = Field(description=""" Mathematical Assumptions that are made. Examples= ["Function f is continuous"]""")
    raw_input: str = Field(description="The raw input .tex file.")



