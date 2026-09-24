from pydantic import BaseModel, Field

class PlannerResult(BaseModel):
    plan: str = Field(description="Plan to solve the given mathematical task.")
