import mlflow
import uuid
from utils.mlflow_utils import create_experiment, get_experiment

if __name__ == "__main__":

    experiment_name = "testing_mlflow_01"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                             artifact_location = artifact_location,
                             tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
    experiment = get_experiment(experiment_id=experiment_id)

    # mlflow.set_experiment(experiment_name=experiment_name)

    # Generate a random UUID (version 4)
    guid = uuid.uuid4()
    run_name = f"run_{guid}"


    with mlflow.start_run(run_name=run_name, experiment_id=experiment.experiment_id) as run:
        # machine learning code goes here
        mlflow.log_param("param1", 5)

    print("MLflow run completed successfully.")

    print(f"Run ID: {run.info.run_id}")
    print(run.info)  # This will print the run info object
    print(f"Run Name: {run.info.run_name}")
    print(f"Run Status: {run.info.status}")
    print(f"Run Artifacts URI: {run.info.artifact_uri}")
    print(f"Run Experiment ID: {run.info.experiment_id}")
    print(f"Run Start Time: {run.info.start_time}")
    print(f"Run End Time: {run.info.end_time}")
    print(f"Run Tags: {run.data.tags}")
    print(f"Run Parameters: {run.data.params}")
    print(f"Run Metrics: {run.data.metrics}")
    print(f"Run Data: {run.data}")
    # print(f"Run Data Schema: {run.data.schema}")
