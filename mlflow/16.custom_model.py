import mlflow
from utils.mlflow_utils import create_experiment, get_experiment


class CustomModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        pass

    def fit(self):
        print("CustomModel fit method called")
        
    def predict(self, model_input):
        return self.get_predictions(model_input)
    
    def get_predictions(self, model_input):
        print("CustomModel get_predictions method called")
        return " ".join([w.upper() for w in model_input])
    
    
if __name__ == "__main__":
    experiment_name = "custom_model_example"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                                       artifact_location=artifact_location,
                                       tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
    experiment = get_experiment(experiment_name=experiment_name)

    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="custom_model_run") as run:
        print(f"Run ID: {run.info.run_id}")
        custom_model = CustomModel()
        custom_model.fit()

        mlflow.pyfunc.log_model("custom_model", python_model=custom_model)
        mlflow.log_param("model_type", "CustomModel")
        
        model_input = ["hello", "world"]
        predictions = custom_model.predict(model_input)
        print(f"Predictions: {predictions}")