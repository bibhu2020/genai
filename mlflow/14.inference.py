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

    run_id= "28431454fef549f1b469f60ef32f31db"
    X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=5, random_state=42)
    X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
    y = pd.DataFrame(y, columns=["target"])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # load the model
    model_uri = f"runs:/{run_id}/model"
    model_uri = f"/home/azureuser/projects/srescripts/pocs/genai/mlflow/_artifacts/testing_mlflow_01/models/m-59c1dccad8f248039eb239fad8c3848c/artifacts"
    model = mlflow.sklearn.load_model(model_uri)
    
    # make predictions
    y_pred = model.predict(X_test)

    y_pred_df = pd.DataFrame(y_pred, columns=["prediction"])

    print(y_pred_df.head())








