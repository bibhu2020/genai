import mlflow
from mlflow import MlflowClient
from utils.mlflow_utils import create_experiment, get_experiment

if __name__ == "__main__":
    experiment_name = "model_registry"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                                       artifact_location=artifact_location,
                                       tags={"purpose": "example", "version": "1.0.0"})
    experiment = get_experiment(experiment_name=experiment_name)

    client = MlflowClient()
    model_name = "registered_model_1"

    # create registerd model
    # client.create_registered_model(name=model_name)

    # create a model version
    # run_id='6262bcbd32d749d0b0010d65293c4b73'
    # client.create_model_version(
    #     name=model_name,
    #     source=f"{artifact_location}/model",
    #     run_id=run_id,
    #     tags={"version": "1.0.0", "purpose": "example"}
    # )

    # transition model version to production
    # client.transition_model_version_stage(
    #     name=model_name,
    #     version=1,
    #     stage="Production",
    #     archive_existing_versions=True
    # )

    # delete model version
    # client.delete_model_version(name=model_name, version=1)

    # delete registered model
    client.delete_registered_model(name=model_name)   
