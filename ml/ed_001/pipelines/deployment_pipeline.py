import os

from pipelines.training_pipeline import ml_pipeline
from steps.dynamic_importer import dynamic_importer
from steps.model_loader import model_loader
from steps.prediction_service_loader import prediction_service_loader
from steps.predictor import predictor
from zenml import pipeline
from zenml.integrations.mlflow.steps import mlflow_model_deployer_step
from utils.config_loader import get_config
config = get_config()

requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")


@pipeline(enable_cache=False, name=config["pipelines"]["continuous_deployment_pipeline"]["name"])
def continuous_deployment_pipeline():
    """Run a training job and deploy an MLflow model deployment."""
    # Re-Run the training pipeline
    # This will return the trained model
    trained_model = ml_pipeline()  # No need for is_promoted return value anymore

    # (Re)deploy the trained model 
    ## workers: Number of workers to use for the deployment service. (used by gunicorn)
    ## deploy_decision: Whether to deploy the model or not.
    ## model: The model to deploy.
    ### This model is automatically registered with MLflow by ZenML.
    ### The model deployment step will deploy the latest version of this model. 
    ### and will make it available for inference. URL: http://localhost:8000/invocations >> MLflow serve (triggered by ZenML)
    mlflow_model_deployer_step(workers=3, deploy_decision=True, model=trained_model)


@pipeline(enable_cache=False, name=config["pipelines"]["inference_pipeline"]["name"])
def inference_pipeline():
    """Run a batch inference job with data loaded from an API."""
    # Load batch data for inference
    batch_data = dynamic_importer()

    # Load the deployed model service
    model_deployment_service = prediction_service_loader(
        pipeline_name=config["pipelines"]["continuous_deployment_pipeline"]["name"],
        step_name="mlflow_model_deployer_step",
    )

    # if model_deployment_service:
    #     print(
    #         f"The MLflow prediction server is running locally as a daemon "
    #         f"process and accepts inference requests at:\n"
    #         f"    {model_deployment_service.prediction_url}\n"
    #         f"To stop the service, re-run the same command and supply the "
    #         f"`--stop-service` argument."
    #     )

    # Run predictions on the batch data
    predictions = predictor(service=model_deployment_service, input_data=batch_data)
    print(f"Inputs: {batch_data}")
    print(f"Predictions: {predictions}")

