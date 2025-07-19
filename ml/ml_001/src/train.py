# File: src/train.py

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from src.data_preprocessing import load_data
import yaml


def train_model(config_path="config/config.yaml"):
    """
    Train a RandomForestRegressor model and log to MLflow.
    """
    # Load config file
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Load training and testing data
    X_train, X_test, y_train, y_test = load_data(config['data']['path'])

    # Create the model using config
    model = RandomForestRegressor(
        n_estimators=config['model']['n_estimators'],
        max_depth=config['model']['max_depth'],
        random_state=config['model']['random_state']
    )

    # Train model
    model.fit(X_train, y_train)

    # Predict on test data
    y_test_pred = model.predict(X_test)

    # Evaluate MSE
    mse = mean_squared_error(y_test, y_test_pred)

    # Log to MLflow
    mlflow.log_param("n_estimators", config['model']['n_estimators'])
    mlflow.log_param("max_depth", config['model']['max_depth'])
    mlflow.log_param("random_state", config['model']['random_state'])
    mlflow.log_metric("mse", mse)
    mlflow.sklearn.log_model(model, "model")

    print(f"Logged MSE: {mse}")
    return model
