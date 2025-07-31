import logging

import pandas as pd
from src.model_dev import (
    HyperparameterTuner,
    LightGBMModel,
    LinearRegressionModel,
    RandomForestModel,
    XGBoostModel,
)
from sklearn.base import RegressorMixin
from zenml import step

# # Create an instance (optional)
# config = ModelNameConfig()

import mlflow
from zenml.client import Client
import joblib

experiment_tracker = Client().active_stack.experiment_tracker


@step(experiment_tracker=experiment_tracker.name)
def train_model(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> RegressorMixin:
    """
    Args:
        x_train: pd.DataFrame
        x_test: pd.DataFrame
        y_train: pd.Series
        y_test: pd.Series
    Returns:
        model: RegressorMixin
    """
    try:
        model = None
        tuner = None

        # if config.model_name == "lightgbm":
        #     # mlflow.lightgbm.autolog()
        #     model = LightGBMModel()
        # elif config.model_name == "randomforest":
        #     # mlflow.sklearn.autolog()
        #     model = RandomForestModel()
        # elif config.model_name == "xgboost":
        #     # mlflow.xgboost.autolog()
        #     model = XGBoostModel()
        # elif config.model_name == "linear_regression":
        if 1==1: 
            mlflow.sklearn.autolog()
            model = LinearRegressionModel()
        else:
            raise ValueError("Model name not supported")

        tuner = HyperparameterTuner(model, x_train, y_train, x_test, y_test)

        if 1==0:
            best_params = tuner.optimize()
            trained_model = model.train(x_train, y_train, **best_params)
        else:
            trained_model = model.train(x_train, y_train)
            joblib.dump(trained_model, "model.joblib")

        logging.info("Model Training completed")
        return trained_model
    except Exception as e:
        logging.error(e)
        raise e
