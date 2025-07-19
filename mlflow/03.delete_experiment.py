from utils.mlflow_utils import delete_experiment

if __name__ == "__main__":
    experiment_name = "testing_mlflow_02"
    experiment = delete_experiment(experiment_name=experiment_name)
    if experiment:
        print(f"Experiment '{experiment_name}' deleted successfully.")
    else:
        print(f"Experiment '{experiment_name}' does not exist or could not be deleted.")    