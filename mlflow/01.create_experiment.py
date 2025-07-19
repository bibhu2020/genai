from utils.mlflow_utils import create_experiment

if __name__ == "__main__":
    # Create an experiment named "My Experiment"
    experiment_name = "testing_mlflow_02"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                             artifact_location = artifact_location,
                             tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
