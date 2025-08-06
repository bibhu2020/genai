# Objective:
This is a learning project to learn how linear regression works using Mlops. The dataset is a past history of sales based on various advertisement mode. Our task is to build a model that could predict the sames base on TV ad expenses.

## Install Required Packages
```bash

conda create --prefix ./.venv python=3.11 -y

conda activate ./.venv

uv pip install -r requirements.txt


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

