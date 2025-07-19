import mlflow
import uuid
from utils.mlflow_utils import create_experiment, get_experiment

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# from sklearn.metrics import accuracy_score, precision_score, recall_score 
# from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay, ConfusionMatrixDisplay

import matplotlib.pyplot as plt

if __name__ == "__main__":
    
    experiment_name = "testing_mlflow_01"
    experiment = get_experiment(experiment_name=experiment_name)
    print(f"Experiment: {experiment.name}")

    # Generate a random UUID (version 4)
    guid = uuid.uuid4()
    run_name = f"run_logging_models_{guid}"

    with mlflow.start_run(run_name=run_name, experiment_id=experiment.experiment_id) as run:

        # create synthetic data
        X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=5, random_state=42)
        # split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=43)

        # do auto logging
        mlflow.autolog()

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mlflow.sklearn.log_model(
            sk_model=model,
            name="random_forest_classifier",
        )

        # print run information
        print(f"Run ID: {run.info.run_id}")
        print(f"Run Name: {run.info.run_name}")
        print(f"Run Status: {run.info.status}")
        print(f"Run Artifacts URI: {run.info.artifact_uri}")
                

        

    print("MLflow run completed successfully.")
    




