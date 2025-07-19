import mlflow
from sklearn.ensemble import RandomForestClassifier
from utils.mlflow_utils import create_experiment, get_experiment


class CustomModel(mlflow.pyfunc.PythonModel):
    def predict(self, model_input, params):
        return model_input;

if __name__ == "__main__":
    experiment_name = "model_registry"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                                       artifact_location=artifact_location,
                                       tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
    experiment = get_experiment(experiment_name=experiment_name)

    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="model_registry_run") as run:
        custom_model = CustomModel()
        mlflow.pyfunc.log_model(
            name="custom_model",
            python_model=custom_model,
            registered_model_name="CustomModel"
        )
        mlflow.sklearn.log_model(
            sk_model=RandomForestClassifier(),
            name="rf_model",
            registered_model_name="RandomForestModel"
        )
        mlflow.sklearn.log_model(
            sk_model=RandomForestClassifier(),
            name="rf_model2"
        )