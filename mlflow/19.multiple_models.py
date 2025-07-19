import mlflow
from utils.mlflow_utils import create_experiment, get_experiment
from mlflow.models.signature import ModelSignature, infer_signature
from sklearn.ensemble import RandomForestClassifier
from mlflow.types.schema import Schema, ColSpec, ParamSpec, ParamSchema

from sklearn.datasets import make_classification
import pandas as pd
from typing import Tuple
import numpy as np


class CustomModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        pass

    def fit(self):
        print("CustomModel fit method called")
        
    # def predict(self, model_input):
    #     return self.get_predictions(model_input)
    
    # def get_predictions(self, model_input):
    #     print("CustomModel get_predictions method called")
    #     return " ".join([w.upper() for w in model_input])

    def predict_model1(self, model_input):
        return 0 * model_input;

    def predict_model2(self, model_input):
        return 1 * model_input;

    
    def predict_model3(self, model_input):
        return 2 * model_input;

    def predict(self, model_input, params):
        if params.get("model_name") == "model_1":
            return self.predict_model1(model_input)
        elif params.get("model_name") == "model_2":
            return self.predict_model2(model_input)
        elif params.get("model_name") == "model_3":
            return self.predict_model3(model_input)
        else:
            raise ValueError(f"Unknown model type: {params.get('model_name')}") 
    
    
if __name__ == "__main__":
    experiment_name = "servinng_multiple_models"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                                       artifact_location=artifact_location,
                                       tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
    experiment = get_experiment(experiment_name=experiment_name)

    input_schema = Schema(inputs=[
        ColSpec(type="integer", name="input")
    ])
    output_schema = Schema(inputs=[
        ColSpec(type="integer", name="output")
    ])
    param_spec = ParamSpec(name="model_name", dtype="string", default=None)
    param_schema = ParamSchema(params=[param_spec])

    model_signature = ModelSignature(inputs=input_schema, outputs=output_schema, params=param_schema)
    # print("Model Signature:")
    # print(model_signature.to_dict())


    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="servinng_multiple_models_run") as run:
        mlflow.pyfunc.log_model(
            name="custom_model",
            python_model=CustomModel(),
            signature=model_signature
        )

        model_uri = f"runs:/{run.info.run_id}/custom_model"
        print(f"Model URI: {model_uri}")
        loaded_model = mlflow.pyfunc.load_model(model_uri=model_uri)

        for n in range(3):
            print(loaded_model.predict(data={"input": np.int32(10)}, params={"model_name": f"model_{n+1}"}))
            print('\n')

        print(f"Model URI: {model_uri}")

# mlflow models serve --model-uri runs:/428c4eee148d4a878279793b5ade420e/custom_model --no-conda --port 8080