import mlflow
from utils.mlflow_utils import create_experiment, get_experiment
from mlflow.models.signature import ModelSignature, infer_signature
from sklearn.ensemble import RandomForestClassifier
from mlflow.types.schema import Schema, ColSpec, ParamSpec, ParamSchema

from sklearn.datasets import make_classification
import pandas as pd
from typing import Tuple

def get_training_data() -> Tuple[pd.DataFrame]:
    X, y = make_classification(n_samples=100, n_features=20, random_state=42)
    features = [f"feature_{i}" for i in range(20)]
    df = pd.DataFrame(X, columns=features)
    df['label'] = y
    return df[features], df['label']


if __name__ == "__main__":
    x_train, y_train = get_training_data()
    print(x_train.head())

    cols_spec = []
    data_map= {
        'int64': 'integer',
        'float64': 'float',
        'str': 'string',
        'bool': 'boolean',
        'date': 'datetime'
    }

    for name, dtype in x_train.dtypes.items():
        col_type = data_map.get(str(dtype), 'string')
        cols_spec.append(ColSpec(col_type, name=name))

    input_schema = Schema(cols_spec)
    output_schema = Schema([ColSpec('integer', name='label')])

    parameter = ParamSpec(name='model_name', dtype='string', default='my_model')
    param_schema = ParamSchema(params=[parameter])
    # print(input_schema)
    # print('\n', output_schema)
    # print('\n', param_schema)

    # Create a model signature (Approach 1 - manual)
    model_signature = ModelSignature(inputs=input_schema, outputs=output_schema, params=param_schema)
    print("Model Signature:")
    print(model_signature.to_dict())
    
    # Infer model signature from training data (Approach 2 - recommended)
    model_signature = infer_signature(x_train, y_train, params={'model_name': 'my_model'})
    print("Inferred Model Signature:")
    print(model_signature.to_dict())

    experiment_name = "model_signature_example"
    artifact_location = f"./_artifacts/{experiment_name}"
    experiment_id = create_experiment(name=experiment_name,
                             artifact_location = artifact_location,
                             tags={"purpose": "example", "version": "1.0.0"})
    print(f"Experiment ID: {experiment_id}")
    experiment = get_experiment(experiment_name=experiment_name)

    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name="model_signature_run") as run:
        print(f"Run ID: {run.info.run_id}")

        mlflow.sklearn.log_model(
            sk_model=RandomForestClassifier(),  # Replace with your trained model
            name="model_signature",
            signature=model_signature
        )

        # mlflow.log_param("model_name", "my_model")
        # mlflow.log_param("input_schema", input_schema.to_dict())
        # mlflow.log_param("output_schema", output_schema.to_dict())
        # mlflow.log_param("param_schema", param_schema.to_dict())
        
        # # Log the model signature
        # mlflow.log_model_signature(model_signature)
        
        # # Optionally, log the training data
        # mlflow.log_artifact("training_data.csv", artifact_path="data")

        # # Save the model signature to a file
        # with open("model_signature.json", "w") as f:
        #     f.write(model_signature.to_json())
        # mlflow.log_artifact("model_signature.json", artifact_path="model_signature")

        # # Log the model signature as a JSON artifact
        # mlflow.log_artifact("model_signature.json", artifact_path="model_signature")
        
    print("Run completed and model signature logged.")
        



    

