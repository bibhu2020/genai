import mlflow
import uuid
from utils.mlflow_utils import create_experiment, get_experiment

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score 
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay, ConfusionMatrixDisplay

import matplotlib.pyplot as plt


if __name__ == "__main__":
    
    experiment_name = "testing_mlflow_01"
    experiment = get_experiment(experiment_name=experiment_name)
    print(f"Experiment: {experiment.name}")

    # Generate a random UUID (version 4)
    guid = uuid.uuid4()
    run_name = f"run_logging_images_{guid}"

    with mlflow.start_run(run_name=run_name, experiment_id=experiment.experiment_id) as run:

        X, y = make_classification(n_samples=1000, n_features=20, n_informative=2, n_redundant=10, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        # log the precision-recall curve
        fig_pr = plt.figure()
        pr_display = PrecisionRecallDisplay.from_predictions(y_test, y_pred, ax=fig_pr.gca())
        plt.title("Precision-Recall Curve")
        plt.legend()

        mlflow.log_figure(fig_pr, "metrics/precision_recall_curve.png")

        # log the ROC curve
        fig_roc = plt.figure()
        roc_display = RocCurveDisplay.from_predictions(y_test, y_pred, ax=fig_roc.gca())
        plt.title("ROC Curve")
        plt.legend()

        mlflow.log_figure(fig_roc, "metrics/roc_curve.png")

        # log the confusion matrix
        fig_cm = plt.figure()
        cm_display = ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, ax=fig_cm.gca())
        plt.title("Confusion Matrix")
        
        mlflow.log_figure(fig_cm, "metrics/confusion_matrix.png")

        # print run information
        print(f"Run ID: {run.info.run_id}")
        print(f"Run Name: {run.info.run_name}")
        print(f"Run Status: {run.info.status}")
        print(f"Run Artifacts URI: {run.info.artifact_uri}")
                

        

    print("MLflow run completed successfully.")
    




