import logging
from typing import Tuple
import pandas as pd
from zenml import step

from src.evaluation import MSE, R2Score, RMSE 
from sklearn.base import RegressorMixin
from typing import Tuple
from typing_extensions import Annotated

import mlflow
from zenml.client import Client
experiment_tracker = Client().active_stack.experiment_tracker


@step(experiment_tracker=experiment_tracker.name)
def evaluate_model(
    model: RegressorMixin,
    X_test: pd.DataFrame,
    y_test: pd.DataFrame
) -> Tuple[
    Annotated[float, "r2"],
    Annotated[float, "mse"],
    Annotated[float, "rmse"],
]:
    """Data cleaning class which preprocesses the data and divides it into train and test data.

    Args:
        data: pd.DataFrame
    """
    try: 
        prediction = model.predict(X_test)
        mse_class = MSE()
        mse = mse_class.calculate_score(y_test, prediction)

        r2_class = R2Score()
        r2 = r2_class.calculate_score(y_test, prediction)

        rmse_class = RMSE()
        rmse = rmse_class.calculate_score(y_test, prediction)
        logging.info("Evaluation completed")
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("rmse", rmse)
        return r2, mse, rmse 
    except Exception as e:
        logging.error("Error in evaluation: {}".format(e))
        raise e