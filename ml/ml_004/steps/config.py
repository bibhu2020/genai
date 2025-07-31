from pydantic import BaseModel

class Config(BaseModel):
    model_name: str = ""
    fine_tuning: bool = False