from pydantic import BaseModel

class ModelNameConfig(BaseModel):
    """Model Configurations"""
    model_name: str = "linear_regression"
    fine_tuning: bool = False
