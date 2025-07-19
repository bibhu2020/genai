import pandas as pd
from sklearn.model_selection import train_test_split

def load_data(path):
    df = pd.read_csv(path)
    X = df.drop("median_house_value", axis=1)
    y = df["median_house_value"]
    return train_test_split(X, y, test_size=0.2, random_state=42)