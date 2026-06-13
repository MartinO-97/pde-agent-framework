from .proof_result import ProofResult
from pydantic import BaseModel

class WriterInput(BaseModel):
    proof: ProofResult
    output_directory: str