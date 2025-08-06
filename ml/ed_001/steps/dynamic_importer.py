import pandas as pd
from zenml import step


@step
def dynamic_importer() -> str:
    """Dynamically imports data for testing out the model."""
    # Here, we simulate importing or generating some data.
    # In a real-world scenario, this could be an API call, database query, or loading from a file.
    data = {
        "TV": [230.1, 44.5],
        "Radio": [37.8, 39.3],
        "Newspaper": [69.2, 45.1],

    }

    df = pd.DataFrame(data)

    # Convert the DataFrame to a JSON string
    json_data = df.to_json(orient="split")

    return json_data
