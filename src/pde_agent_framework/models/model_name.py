from pydantic import BaseModel, Field

class ModelName(BaseModel):
    model_name: str = Field(description="The model name used to gnerate the proof")