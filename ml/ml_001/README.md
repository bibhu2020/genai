# Folder Structure

## src/ - Core Logic
train.py: Logs model, parameters, and metrics to MLflow.

mlflow_utils.py: Wraps MLflow logging (mlflow.log_metric, etc.).

evaluate.py: Evaluates and logs test set metrics, possibly confusion matrix as an artifact.

predict.py: Inference script, loads models from MLflow model registry.

## Optional - Add Ons
tests/ – Unit tests using pytest

scripts/ – Shell scripts for automating runs or deployments

experiments/ – YAML/JSON configs for hyperparameter tuning

deployment/ – Flask/FastAPI or MLflow model serving