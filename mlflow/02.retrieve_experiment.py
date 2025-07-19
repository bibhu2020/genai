from utils.mlflow_utils import get_experiment_by_name

if __name__ == "__main__":
    # Create an experiment named "My Experiment"
    experiment_name = "Default"
    experiment = get_experiment_by_name(experiment_name=experiment_name)
    print(f"Experiment ID: {experiment.experiment_id}")
    print(f"Experiment Name: {experiment.name}")
    print(f"Artifact Location: {experiment.artifact_location}")
    print(f"Tags: {experiment.tags}")
    print(f"Lifecycle Stage: {experiment.lifecycle_stage}")
    print(f"Creation Time: {experiment.creation_time}")
    print(f"Last Updated Time: {experiment.last_update_time}")