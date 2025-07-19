import mlflow
from typing import Any

def create_experiment(name: str, artifact_location: str, tags: dict[str, Any] = None) -> int:
    """
    Create a new MLflow experiment.

    :param name: Name of the experiment.
    :param artifact_location: Location to store artifacts for the experiment.
    :param tags: Optional tags to associate with the experiment.
    :return: The ID of the created experiment.
    """
    try:
        experiment_id = mlflow.create_experiment(name=name, artifact_location=artifact_location, tags=tags)
    except mlflow.exceptions.MlflowException as e:
        print(f"Error creating experiment: {e}")
        experiment_id = mlflow.get_experiment_by_name(name).experiment_id if mlflow.get_experiment_by_name(name) else None

    if experiment_id is None:
        raise ValueError(f"Failed to create or retrieve experiment with name: {name}")

    print(f"Experiment created with ID: {experiment_id}")


    return experiment_id

def get_experiment(experiment_id: int = None, experiment_name: str = None) -> mlflow.entities.Experiment:
    """
    Retrieve an MLflow experiment by its name.

    :param name: Name of the experiment.
    :return: The MLflow Experiment object.
    """
    if experiment_id is not None:
        experiment = mlflow.get_experiment(experiment_id)
    elif experiment_name is not None:
        experiment = mlflow.get_experiment_by_name(experiment_name)
    else:
        raise ValueError("Either 'experiment_id' or 'experiment_name' must be provided.")
    
    return experiment

def delete_experiment(experiment_id: int=None, experiment_name: str=None) -> None:
    """
    Delete an MLflow experiment by its ID or name.

    :param experiment_id: ID of the experiment to delete.
    :param experiment_name: Name of the experiment to delete.
    """
    if experiment_id is not None:
        mlflow.delete_experiment(experiment_id)
    elif experiment_name is not None:
        exp = get_experiment_by_name(experiment_name=experiment_name)
        if exp:
            delete_experiment(experiment_id=exp.experiment_id)
        else:
            raise ValueError(f"Experiment with name '{experiment_name}' does not exist.")
    else:
        raise ValueError("Either 'experiment_id' or 'experiment_name' must be provided.")   
