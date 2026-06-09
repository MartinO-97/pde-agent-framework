from pydantic import BaseModel

r""" Class that defines the output scheme of the extractor agent """

class ProblemSummary(BaseModel):
    task: str
    mathematical_objects: list[str]
    allowed_lemmas_and_theorems: list[str]
    assumptions: list[str]



