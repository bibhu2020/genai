import mlflow
import uuid
from utils.mlflow_utils import create_experiment, get_experiment

if __name__ == "__main__":
    
    experiment_name = "testing_mlflow_01"
    experiment = get_experiment(experiment_name=experiment_name)
    print(f"Experiment: {experiment.name}")

    # Generate a random UUID (version 4)
    guid = uuid.uuid4()
    run_name = f"run_logging_metrics_{guid}"

    with mlflow.start_run(run_name=run_name, experiment_id=experiment.experiment_id) as run:
        # machine learning code goes here
        mlflow.log_param("learning_rate", 0.01)

        paramertes = {
            "batch_size": 32,
            "epochs": 10,
            "optimizer": "adam"
        }

        mlflow.log_params(paramertes)

        mlflow.log_metric("accuracy", 0.95)
        metrics = {
            "loss": 0.05,
            "precision": 0.90,
            "recall": 0.85
        }
        mlflow.log_metrics(metrics)

        

        # print run information
        print(f"Run ID: {run.info.run_id}")
        print(f"Run Name: {run.info.run_name}")
        print(f"Run Status: {run.info.status}")
        print(f"Run Artifacts URI: {run.info.artifact_uri}")
        print(f"Run Experiment ID: {run.info.experiment_id}")
        print(f"Run Start Time: {run.info.start_time}")
        print(f"Run End Time: {run.info.end_time}")
        print(f"Run Tags: {run.data.tags}")
        print(f"Run Parameters: {run.data.params}")
        print(f"Run Metrics: {run.data.metrics}")
        print(f"Run lifecycle_stage: {run.info.lifecycle_stage}")

    print("MLflow run completed successfully.")
    




