import json
import os
import numpy as np
import pandas as pd
from materializer.custom_materializer import cs_materializer
from zenml import pipeline, step
from zenml.config import DockerSettings
from zenml.constants import DEFAULT_SERVICE_START_STOP_TIMEOUT
from zenml.integrations.constants import MLFLOW
from zenml.integrations.mlflow.model_deployers.mlflow_model_deployer import (
    MLFlowModelDeployer,
)
from zenml.integrations.mlflow.services import MLFlowDeploymentService
from zenml.integrations.mlflow.steps import mlflow_model_deployer_step
from pydantic import BaseModel

from steps.clean_data import clean_data
from steps.evaluate_model import evaluate_model
from steps.ingest_data import ingest_data
from steps.train_model import train_model

# from zenml.config import DockerSettings
# # from zenml.enums import PythonPackageInstaller
# docker_settings = DockerSettings(
#     python_package_installer="pip",
#     required_integrations=[MLFLOW]
# )

class DeploymentTriggerConfig(BaseModel):
    """Parameters that are used to trigger the deployment"""
    min_accuracy: float = 0.9


@step
def deployment_trigger(
    accuracy: float,
    config: DeploymentTriggerConfig,
) -> bool:
    """Implements a simple model deployment trigger that looks at the
    input model accuracy and decides if it is good enough to deploy"""

    return accuracy > config.min_accuracy

@pipeline(enable_cache=False, name="ml_004_model_deploy")
def continuous_deployment_pipeline1(
    min_accuracy: float = 0.9,
    workers: int = 1,
    timeout: int = DEFAULT_SERVICE_START_STOP_TIMEOUT,
):
    """
    Args:
        min_accuracy: float
        workers: int
        workers: int
    Returns:
        None
    """
    # Link all the steps artifacts together
    data = ingest_data()
    X_train, X_test, y_train, y_test= clean_data(data)
    model = train_model(x_train=X_train, x_test=X_test, y_train=y_train, y_test=y_test)
    r2, mse, rmse =evaluate_model(model, X_test, y_test)

    # return r2, mse, rmse

    deployment_decision = deployment_trigger(accuracy=mse, 
                                             config=DeploymentTriggerConfig(min_accuracy=min_accuracy)
                                             )
    mlflow_model_deployer_step(
        model=model,
        deploy_decision=deployment_decision,
        workers=workers,
        timeout=timeout,
    )


@pipeline(enable_cache=False, name="ml_004_model_deploy")
def continuous_deployment_pipeline(
    min_accuracy: float = 0.9,
    workers: int = 1,
    timeout: int = DEFAULT_SERVICE_START_STOP_TIMEOUT,
):
    # Link all the steps artifacts together
    df = ingest_data()
    x_train, x_test, y_train, y_test = clean_data(data=df)
    model = train_model(x_train, x_test, y_train, y_test)
    r2, mse, rmse = evaluate_model(model, x_test, y_test)
    deployment_decision = deployment_trigger(accuracy=mse, 
                                             config=DeploymentTriggerConfig(min_accuracy=min_accuracy)
                                             )
    mlflow_model_deployer_step(
        model=model,
        deploy_decision=deployment_decision,
        workers=workers,
        timeout=timeout,
    )