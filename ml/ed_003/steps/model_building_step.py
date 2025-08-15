import logging
import mlflow
import pandas as pd
import numpy as np

from typing import Annotated
from zenml import Model
from sklearn.base import RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    LabelEncoder, 
    OrdinalEncoder,
    FunctionTransformer, 
    StandardScaler, 
    MinMaxScaler
)
from zenml import ArtifactConfig, step
from zenml.enums import ArtifactType
from zenml.client import Client
from utils.config_loader import get_config
config = get_config()

# Get the active experiment tracker from ZenML
experiment_tracker = Client().active_stack.experiment_tracker
if not experiment_tracker:
    raise ValueError("No active experiment tracker found. Please set up an experiment tracker in your ZenML stack.")


model = Model(
    name=config["model"]["name"],
    version=config["model"]["version"],
    license=config["model"]["license"],
    description=config["model"]["description"],
    tags=config["model"]["tags"],
)


@step(enable_cache=False, 
      experiment_tracker=experiment_tracker.name, 
      model=model)
def model_building_step(
    X_train: pd.DataFrame, y_train: pd.Series,
    algorithm: str = "linear_regression"
) -> Annotated[Pipeline, ArtifactConfig(name="sklearn_pipeline", artifact_type=ArtifactType.MODEL)]:
    """
    Builds and trains a Linear Regression model using scikit-learn wrapped in a pipeline.

    Parameters:
    X_train (pd.DataFrame): The training data features.
    y_train (pd.Series): The training data labels/target.

    Returns:
    Pipeline: The trained scikit-learn pipeline including preprocessing and the Linear Regression model.
    """

    # Ensure the inputs are of the correct type
    if not isinstance(X_train, pd.DataFrame):
        raise TypeError("X_train must be a pandas DataFrame.")
    if not isinstance(y_train, pd.Series):
        raise TypeError("y_train must be a pandas Series.")

    # Identify categorical and numerical columns
    categorical_cols = X_train.select_dtypes(include=["object", "category"]).columns
    numerical_cols = X_train.select_dtypes(exclude=["object", "category"]).columns

    logging.info(f"Categorical columns: {categorical_cols.tolist()}")
    logging.info(f"Numerical columns: {numerical_cols.tolist()}")

    # Define preprocessing for categorical and numerical features
    numerical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),  # your imputer
            ("log", FunctionTransformer(np.log1p, validate=True)),  # add this first
            # ("z-scaler", StandardScaler()),  # add this first
            # ("minmax", MinMaxScaler()),  # add this first
        ]
    )
    # numerical_transformer = SimpleImputer(strategy="mean") #this may not take any action because we already handled missing values in the preprocessing. this is a safety net.
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            # ("onehot_encoder", OneHotEncoder(handle_unknown="ignore")),
            # ("label_encoder", LabelEncoder()),
            ("label_encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]
    )

    # Bundle preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ("numerical_cols", numerical_transformer, numerical_cols),
            ("categorical_cols", categorical_transformer, categorical_cols),
        ]
    )

    # Define the model training pipeline
    if algorithm == "linear_regression":
        logging.info("Using Linear Regression algorithm.")
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", LinearRegression())])
    elif algorithm == "logistic_regression":
        logging.info("Using Logistic Regression algorithm.")
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", LogisticRegression(max_iter=1000))])
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Use 'linear_regression' or 'logistic_regression'.")
    

    # Start an MLflow run to log the model training process
    print("zenml will automatically start a run if there is no active run. this is just a safety net.")
    if not mlflow.active_run(): 
        mlflow.start_run()  # Start a new MLflow run if there isn't one active

    try:
        # Enable autologging for scikit-learn to automatically capture model metrics, parameters, and artifacts
        # mlflow.set_experiment(experiment_tracker.name)  # <- custom experiment name
        mlflow.sklearn.autolog()

        logging.info("Building and training the Linear Regression model.")
        pipeline.fit(X_train, y_train)
        logging.info("Model training completed.")

        # Log the columns/inputs that the model expects
        # Detect which encoder is in use for categorical features
        cat_transformer = pipeline.named_steps["preprocessor"].transformers_[1][1]

        expected_columns = numerical_cols.tolist()

        if "onehot_encoder" in cat_transformer.named_steps:
            # Handle OneHotEncoder
            onehot_encoder = cat_transformer.named_steps["onehot_encoder"]
            onehot_encoder.fit(X_train[categorical_cols])
            expected_columns += list(onehot_encoder.get_feature_names_out(categorical_cols))
        elif "label_encoder" in cat_transformer.named_steps or "ordinal_encoder" in cat_transformer.named_steps:
            # Handle OrdinalEncoder or LabelEncoder
            # No expansion of columns, just add categorical names
            expected_columns += categorical_cols.tolist()
        else:
            logging.warning("No known categorical encoder found; categorical columns may be missing from expected_columns.")


        logging.info(f"Model expects the following columns: {expected_columns}")

    except Exception as e:
        logging.error(f"Error during model training: {e}")
        raise e

    finally:
        # End the MLflow run
        print("Model training completed.... ")
        # mlflow.end_run()

    return pipeline
