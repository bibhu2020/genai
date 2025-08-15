# Objective:
This is a learning project to learn how linear regression works using Mlops. The dataset is a past history of housing price. This machine learning is going to predict house price.

## Install Required Packages
```bash

conda create --prefix ./.venv python=3.11 -y

conda activate ./.venv

uv pip install -r requirements.txt


```

## Link the app to zenml and mlflow
```bash
zenml init

zenml project set default

zenml integration install mlflow -y

zenml experiment-tracker register ed002_tracker --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token"

zenml model-deployer register ed002_model --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" 

zenml stack register ed002_stack -a minio_store -o default -d ed002_model -e ed002_tracker --set

```

## How to Run?

```bash
# Run the machine learning pipeline
## This does preprocessing, feature engineering, model training, and storing the model in mlflow artifacts store.
python run_pipeline.py

# Deploy the machine learning model
## This invokes run_pipeline.py to build the model like previous step.
## It then starts a REST API service exposing the model for prediction. 
## It hosts the service on mlflow server itself, and exposes at http://localhost:5000/http://localhost:5000/invocations
python run_deployment.py

# Stop the Deployed Service
python run_deployment.py --stop-service

# Register the machine learning model
## It registers the recent model to the mlflow registry for production use.
python run_registration.py

```

## Production Use
Once the model is reigstered in the mlflow registry, you can start a CD pipeline that would download the model *.pkl file from mlflow registry, package it in a Docker container and deploy to Kubernetes cluster for production use.

