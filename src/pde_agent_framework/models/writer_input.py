from .prover_result import ProverResult
from pydantic import BaseModel, Field

class WriterInput(BaseModel):
    proof: ProverResult = Field(description="The result of the ProverAgent")
    output_directory: str = Field(description="The output directory path")