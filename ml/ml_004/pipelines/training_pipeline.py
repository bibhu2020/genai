from zenml.config import DockerSettings
from zenml.integrations.constants import MLFLOW
from zenml.pipelines import pipeline
from steps.clean_data import clean_data
from steps.ingest_data import ingest_data
from steps.train_model import train_model
from steps.evaluate_model import evaluate_model

# from zenml.config import DockerSettings
# # from zenml.enums import PythonPackageInstaller
# docker_settings = DockerSettings(
#     python_package_installer="pip",
#     required_integrations=[MLFLOW]
# )

@pipeline(enable_cache=False)
def train_pipeline():
    """
    Args:
        ingest_data: DataClass
        clean_data: DataClass
        model_train: DataClass
        evaluation: DataClass
    Returns:
        mse: float
        rmse: float
    """
    df = ingest_data()
    X_train, X_test, y_train, y_test= clean_data(df)
    model = train_model(x_train=X_train, x_test=X_test, y_train=y_train, y_test=y_test)
    r2, mse, rmse =evaluate_model(model, X_test, y_test)

    return r2, mse, rmse
