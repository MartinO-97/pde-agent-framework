from pydantic import BaseModel, Field

class ProverReviewerOutput(BaseModel):
    previous_proofs: list[str] = Field(description="List of previous proofs.") 
    error_name: list[str] = Field(description="List of error names. Error names must be short and clear names.")
    error_description: list[str] = Field(description="Description of the error. Should explain in a few words, what was wrong.")
    proof_ok: bool = Field(description="If the proof is okay, this attribute is set to True, otherwise to False.")
    #iterations: int = Field(description="Number of iterations.") 