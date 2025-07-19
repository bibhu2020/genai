import json
import requests

data = {
    "dataframe_split": {"columns": ["input"], "data": [10]},
    "params": {"model_name": "model_3"}
}

headers = {
    "Content-Type": "application/json"
    }

endpoint = "http://localhost:8080/invocations"

response = requests.post(endpoint, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.json())
# Expected output: {"output": [10]}