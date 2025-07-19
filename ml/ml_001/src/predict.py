import mlflow.sklearn
import pandas as pd

def predict(sample_data):
    model = mlflow.sklearn.load_model("models:/HousingModel/Production")
    df = pd.DataFrame([sample_data])
    prediction = model.predict(df)
    return prediction[0]