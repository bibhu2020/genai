import mlflow
import uuid
from utils.mlflow_utils import create_experiment, get_experiment

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# from sklearn.metrics import accuracy_score, precision_score, recall_score 
# from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay, ConfusionMatrixDisplay

import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":

    experiment_name = "nested_mlflow_01"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                             artifact_location = artifact_location,
                             tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
    experiment = get_experiment(experiment_name=experiment_name)

    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="parent") as parent:
        print(f"Parent Run ID: {parent.info.run_id}")
        mlflow.log_param("parent_param", "parent_value")
        
        with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="child_1", nested=True) as child_1:
            print(f"Child 1 Run ID: {child_1.info.run_id}")
            mlflow.log_param("child_1_param", "child_1_value")

            with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="child_1_subchild", nested=True) as child_1_subchild:
                print(f"Child 1 Subchild Run ID: {child_1_subchild.info.run_id}")
                mlflow.log_param("child_1_subchild_param", "child_1_subchild_value")
            
            with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="child_1_subchild_2", nested=True) as child_1_subchild_2:
                print(f"Child 1 Subchild 2 Run ID: {child_1_subchild_2.info.run_id}")
                mlflow.log_param("child_1_subchild_2_param", "child_1_subchild_2_value")

        with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="child_2", nested=True) as child_2:
            print(f"Child 2 Run ID: {child_2.info.run_id}")
            mlflow.log_param("child_2_param", "child_2_value")
            
            









