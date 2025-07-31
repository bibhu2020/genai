import logging

import pandas as pd
from zenml import step
from typing_extensions import Annotated

class IngestData:
    """
    Data ingestion class which ingests data from the source and returns a DataFrame.
    """

    def __init__(self) -> None:
        """Initialize the data ingestion class."""
        pass

    def get_data(self) -> pd.DataFrame:
        print('reading data....')
        df = pd.read_csv("./data/olist_customers_dataset.csv")
        return df


@step(enable_cache=False)
def ingest_data() -> pd.DataFrame:
    """
    Args:
        None
    Returns:
        df: pd.DataFrame
    """
    try:
        ingestor = IngestData()
        data = ingestor.get_data()

        logging.info("Dataframe shape: %s", data.shape)
        logging.info("Ingestion completed")
        return data
    except Exception as e:
        logging.error(e)
        raise e
