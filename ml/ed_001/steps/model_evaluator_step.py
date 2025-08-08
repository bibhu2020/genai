import logging
import pandas as pd
import mlflow  # Import mlflow here
from zenml.client import Client

from typing import Tuple
from sklearn.pipeline import Pipeline
from src.model_evaluator import ModelEvaluator, RegressionModelEvaluationStrategy
from zenml import step

# Get the active experiment tracker from ZenML
experiment_tracker = Client().active_stack.experiment_tracker
if not experiment_tracker:
    raise ValueError("No active experiment tracker found. Please set up an experiment tracker in your ZenML stack.")

@step(enable_cache=False,
      experiment_tracker=experiment_tracker.name)
def model_evaluator_step(
    trained_model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> Tuple[dict, float]:
    """
    Evaluates the trained model using ModelEvaluator and RegressionModelEvaluationStrategy.

    Parameters:
    trained_model (Pipeline): The trained pipeline containing the model and preprocessing steps.
    X_test (pd.DataFrame): The test data features.
    y_test (pd.Series): The test data labels/target.

    Returns:
    dict: A dictionary containing evaluation metrics.
    """
    # Ensure the inputs are of the correct type
    if not isinstance(X_test, pd.DataFrame):
        raise TypeError("X_test must be a pandas DataFrame.")
    if not isinstance(y_test, pd.Series):
        raise TypeError("y_test must be a pandas Series.")

    logging.info("Applying the same preprocessing to the test data.")

    # Apply the preprocessing and model prediction
    X_test_processed = trained_model.named_steps["preprocessor"].transform(X_test)

    # Initialize the evaluator with the regression strategy
    evaluator = ModelEvaluator(strategy=RegressionModelEvaluationStrategy())

    # Perform the evaluation
    evaluation_metrics = evaluator.evaluate(
        trained_model.named_steps["model"], X_test_processed, y_test
    )

    # Ensure that the evaluation metrics are returned as a dictionary
    if not isinstance(evaluation_metrics, dict):
        raise ValueError("Evaluation metrics must be returned as a dictionary.")
    
    # Log metrics to MLflow with active run
    print("zenml will automatically start a run if there is no active run. this is just a safety net.")
    if not mlflow.active_run(): 
        mlflow.start_run()  # Start a new MLflow run if there isn't one active

    for metric_name, metric_value in evaluation_metrics.items():
        if isinstance(metric_value, (int, float)):
            print(f"Logging metric > {metric_name}: {metric_value}")
            mlflow.log_metric(f"test_{metric_name.lower().replace(' ', '_')}", metric_value)
        else:
            logging.warning(f"Skipping logging of non-numeric metric {metric_name}")

    mse = evaluation_metrics.get("Mean Squared Error", None)
    return evaluation_metrics, mse
