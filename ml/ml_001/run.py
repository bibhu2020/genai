# File: run_experiment.py

import yaml
from src.train import train_model
from src.evaluate import evaluate_model
from src.data_preprocessing import load_data
from src.utils.mlflow_utils import start_run, end_run, log_params, log_metrics, log_model, create_experiment, get_experiment

def load_config(path: str = "config/config.yaml") -> dict:
    """
    Load configuration YAML file.
    """
    with open(path, "r") as file:
        return yaml.safe_load(file)


def main():
    # Load config
    config = load_config()

    # Create or get experiment
    experiment_name = "housing_price_prediction" #config["experiment"]["name"]
    artifact_location = f"./_artifacts/{experiment_name}" #config["experiment"]["artifact_location"] + "/" + experiment_name
    tags = config.get("experiment", {}).get("tags", {})

    experiment_id = create_experiment(name=experiment_name, artifact_location=artifact_location, tags=tags)
    experiment = get_experiment(experiment_id=experiment_id)

    print(f"Using experiment: {experiment.name} with ID: {experiment.experiment_id}")

    # Start MLflow run
    start_run(experiment_name=experiment_name)

    # Train model
    model = train_model()

    # Log model
    log_model(model)

    # Evaluate model
    eval_metrics = evaluate_model(model)
    log_metrics(eval_metrics)

    # End run
    end_run()


if __name__ == "__main__":
    main()
