from pydantic import BaseModel

class PlannerResult(BaseModel):
    plan: str
    task: str