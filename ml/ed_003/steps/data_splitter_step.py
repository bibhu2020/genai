from typing import Tuple

import pandas as pd
from src.data_splitter import DataSplitter, SimpleTrainTestSplitStrategy, StratifiedTrainTestSplitStrategy
from zenml import step


@step
def data_splitter_step(
    df: pd.DataFrame, 
    strategy: str = "simple", 
    target_column: str = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Splits the data into training and testing sets using DataSplitter and a chosen strategy."""

    
    if strategy.lower() == "stratified":
        splitter = DataSplitter(strategy=StratifiedTrainTestSplitStrategy())
    else:
        splitter = DataSplitter(strategy=SimpleTrainTestSplitStrategy())
    
    X_train, X_test, y_train, y_test = splitter.split(df, target_column)
    return X_train, X_test, y_train, y_test
