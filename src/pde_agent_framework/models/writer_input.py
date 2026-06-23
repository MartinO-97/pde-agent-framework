from .prover_result import ProverResult
from pydantic import BaseModel

class WriterInput(BaseModel):
    proof: ProverResult
    output_directory: str