# Starting Zenml and MLflow Server
```bash
docker compose up -d

```

# Onboard an App to ZenML and Mlflow

```bash
cd ~
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

sha256sum Miniconda3-latest-Linux-x86_64.sh

bash Miniconda3-latest-Linux-x86_64.sh

source ~/.bashrc

conda --version


```

## Create a virtual evironment in the app folder (optional)
```bash
conda create --prefix ./.venv python=3.11 -y
conda activate ~/ws/genai/ml/ml_004/.venv
uv pip install -r requirements.txt
```

## Install Required Packages
```bash
uv pip install mlflow==2.15.1
uv pip install zenml[server]==0.84.0

```

## Connect your app to zenml server
this creates a .zen folder in your application folder
```bash
zenml login #this prompts for device authorization

zenml init
```

## Connect zenml to mlflow
This enables the zenml to speak with mlflow server started above.
```bash
# Optional: incase mlflow needs a login. 
# export MLFLOW_TRACKING_USERNAME=your_username
# export MLFLOW_TRACKING_PASSWORD=your_password
# export MLFLOW_TRACKING_URI=http://localhost:5000

#Step1: install zenml integration plugin for mlflow
zenml integration install mlflow -y
#Step2: registers a new experiment in mlflow (name: ml004_tracker). --flavor=mlflow tells the backend mlflow
zenml experiment-tracker register ml004_tracker --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" #Step3: Registers a model deployer component (name: ml004_model). --flavor=mlflow tells the backend mlflow
zenml model-deployer register ml004_model --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" 
#Step4: Registers a full ZenML stack — a combination of components like orchestrator, artifact store, experiment tracker, etc. 
## -a default: Sets the artifact store to the default (often local).
## -o default: Sets the orchestrator to the default (e.g., local or airflow).
## -d ml004_model: Uses the model deployer named ml004_model (registered in step 3).
## -e ml004_tracker: Uses the experiment tracker named ml004_tracker (from step 2).
## --set: Sets this stack as the active stack for future runs.
zenml stack register ml004_stack -a default -o default -d ml004_model -e ml004_tracker --set
```

## Delete a stack from zenml
```bash
zenml stack set default
zenml experiment-tracker delete ml004_tracker
zenml model-deployer delete ml004_model
zenml stack delete -y ml004_stack
```

## Register minio as the artifacts store
before doing this, create a bucket "zenmlartifacts" in minio
```bash
zenml artifact-store delete minio_store


zenml artifact-store register minio_store --flavor s3 --path="s3://zenmlartifacts" --endpoint_url="http://localhost:9000" --access_key="minioadmin" --secret_key="minioadmin"
```

## Zenml Artifacts access from local browser and github
Add the following variables in Github environment variable and local machine environment variables
```
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:9000/
```