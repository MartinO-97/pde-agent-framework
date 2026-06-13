from pydantic import BaseModel

class ProofResult(BaseModel):
    proof: str
    proof_name: str