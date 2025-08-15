import click
from pipelines.deployment_pipeline import (
    continuous_deployment_pipeline,
    inference_pipeline,
)
from rich import print
from zenml.integrations.mlflow.mlflow_utils import get_tracking_uri
from zenml.integrations.mlflow.model_deployers.mlflow_model_deployer import (
    MLFlowModelDeployer,
)
from utils.config_loader import get_config
config = get_config()

@click.command()
@click.option(
    "--stop-service",
    is_flag=True,
    default=False,
    help="Stop the prediction service when done",
)
def run_main(stop_service: bool):
    """Run the prices predictor deployment pipeline"""
    model_name = config["model"]["name"]
    print(f"Running the continuous deployment pipeline for model: {model_name}")

    if stop_service:
        print("Stopping the prediction service...")
        # Get the MLflow model deployer stack component
        model_deployer = MLFlowModelDeployer.get_active_model_deployer()

        # Fetch existing services with same pipeline name, step name, and model name
        existing_services = model_deployer.find_model_server(
            pipeline_name=config["pipelines"]["continuous_deployment_pipeline"]["name"],
            pipeline_step_name="mlflow_model_deployer_step",
            model_name="model", #model_name,
            running=True,
        )

        if existing_services:
            service = existing_services[0]
            print("Model service is running at:", service.prediction_url)
            print("Stopping the service...")
            existing_services[0].stop(timeout=10)
        else:
            print("No running model service found.")        

        return

    # Run the continuous deployment pipeline
    continuous_deployment_pipeline()

    # Run the inference pipeline
    inference_pipeline()

    # print(
    #     "Now run \n "
    #     f"    mlflow ui --backend-store-uri {get_tracking_uri()}\n"
    #     "To inspect your experiment runs within the mlflow UI.\n"
    #     "You can find your runs tracked within the `mlflow_example_pipeline`"
    #     "experiment. Here you'll also be able to compare the two runs."
    # )

    # # Get the active model deployer
    # model_deployer = MLFlowModelDeployer.get_active_model_deployer()

    # # Fetch existing services with the same pipeline name, step name, and model name
    # service = model_deployer.find_model_server(
    #     pipeline_name=config["pipelines"]["continuous_deployment_pipeline"]["name"],
    #     pipeline_step_name="mlflow_model_deployer_step",
    # )

    # if service[0]:
    #     print(
    #         f"The MLflow prediction server is running locally as a daemon "
    #         f"process and accepts inference requests at:\n"
    #         f"    {service[0].prediction_url}\n"
    #         f"To stop the service, re-run the same command and supply the "
    #         f"`--stop-service` argument."
    #     )


if __name__ == "__main__":
    run_main()
