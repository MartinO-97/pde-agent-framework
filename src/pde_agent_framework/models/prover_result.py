from pydantic import BaseModel, Field

class ProverResult(BaseModel):
    proof: str = Field(description="The proof.")
    proof_name: str = Field(description="Name of the proof.")