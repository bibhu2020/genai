import pandas as pd
from zenml import step


@step
def dynamic_importer() -> str:
    """Dynamically imports data for testing out the model."""
    # Here, we simulate importing or generating some data.
    # In a real-world scenario, this could be an API call, database query, or loading from a file.
    data = {
        "Gender": ["Female", "Female", "Male"],
        "Age": [58, 26, 34],
        "Estimated": [95000, 80000, 115000],
        "Purchased": ["Yes", "No", "No"],
    }

    df = pd.DataFrame(data)

    # Convert the DataFrame to a JSON string
    json_data = df.to_json(orient="split")

    return json_data
