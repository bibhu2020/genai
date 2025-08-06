# Objective
Objective of this project is to setup the MLOps tools using docker compose, and run them from the local machine. Also, integrate the MLOPs tools with github execute the Machine Learning pipelines and experiments through CI/CD pipelines.

It installs the following tools:
- zenml - ML pipeline tracker
- mlflow - ML experiment tracker.

## Pre-requisites
- Ubuntu OS
- Docker & Docker Compose
- python installed

## Start the server
```bash
. ./start.sh
```
When you setup the server, it may fail for the first time. To make it work, you will have to do the followings:

1. Both mlflow and zenml stores configuration in mysql. Hence, make sure that the mysql in the docker has 2 dbs in the name zenml & mlflow_db. You can verify this by starting the docker in interactive mode. if the dbs are not present, created them under the root user.

2. Both mlflow and zenml stores the artifacts in minio (a AWS s3 storage simulator). Hence, login to minio http://localhost:9000 (userid/password: minioadmin/minioadmin) and create 2 buckets mlflowartifacts and zenmlartifacts.

3. Once this is done, restart the server `. ./start.sh`.

This will make both zenml and mlflow accessible to you.

*   It makes the zenml server availabe to you on http://127.0.0.1:8237/. On first login, it creates the userid and password.

*   mlflow server available on http://127.0.0.1:5000. It's access is annonymous.


## Onboard an App to Zenml and Mlflow

**Step1**: (optional) Install conda on the machine
```bash
cd ~
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

sha256sum Miniconda3-latest-Linux-x86_64.sh

bash Miniconda3-latest-Linux-x86_64.sh

source ~/.bashrc

conda --version
```

**Step2**: (optional) Create conda virtual environment in the project folder, and install the required packages.
```bash
conda init
conda create --prefix ./.venv python=3.11 -y
conda activate ~/ws/genai/ml/ml_004/.venv
uv pip install -r requirements.txt
uv pip install mlflow==2.15.1
uv pip install zenml[server]==0.84.0
```

**Step3**: Connect your project to zenml from local machine. 

When you are executing the ml pipelines in the local machine, You must run `zenml login`. This prompt you to login tp the zenml and stores the credential in the local machine for the project to connect to the ZENML server on subsequent calls.

After successful login, run `zenml init` command that creates `.zen` sub-folder in the project folder. This is where it stores the zenml related configuration. Hence, you must make sure that this folder is checked-in to the github.

**Step4**: Connect your project to zenml from github.

In case you are executing the ml pipelines from github action, you must set the following secrets in github. 

ZENML_STORE_API_KEY="follow the step5 to create API key"
ZENML_STORE_URL=http://localhost:8237

Note: With the same name ZENML_STORE_URL, a environment variable is also created in the docker for Zenml to establish connection with mysql. `ZENML_STORE_URL=mysql://root:password@mysql:3306/zenml`.

**Step5**: Create ZENML API Key (for github to use)
The API key is created from the local machine. Say, we are creating it for a service account called "zenml_github_sa".
```bash
zenml login

zenml service-account create zenml_github_sa #this generates a key on the command prompt. 
```

## Setup Project Configuration in ZENML
This enables the zenml to speak with mlflow server started above.
```bash
# Optional: incase mlflow needs a login. 
# export MLFLOW_TRACKING_USERNAME=your_username
# export MLFLOW_TRACKING_PASSWORD=your_password
# export MLFLOW_TRACKING_URI=http://localhost:5000
```

**Step1**: install zenml integration plugin for mlflow

```bash
zenml integration install mlflow -y
```

**Step2**: registers a new experiment in mlflow (name: ml004_tracker). --flavor=mlflow tells the backend mlflow
```bash
zenml experiment-tracker register ml004_tracker --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" 
```

**Step3**: Registers a model deployer component (name: ml004_model). --flavor=mlflow tells the backend mlflow

```bash
zenml model-deployer register ml004_model --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" 
```

**Step4**: Registers a full ZenML stack — a combination of components like orchestrator, artifact store, experiment tracker, etc. 

```bash
## -a default: Sets the artifact store to the default (often local).
## -o default: Sets the orchestrator to the default (e.g., local or airflow).
## -d ml004_model: Uses the model deployer named ml004_model (registered in step 3).
## -e ml004_tracker: Uses the experiment tracker named ml004_tracker (from step 2).
## --set: Sets this stack as the active stack for future runs.
zenml stack register ml004_stack -a default -o default -d ml004_model -e ml004_tracker --set
```

**Step5**: Replace the default artifacts store with minio
```bash
zenml integration install s3

# register minio as artifacts store
zenml artifact-store register minio_store --flavor s3 --path="s3://zenmlartifacts" --endpoint_url="http://localhost:9000" --access_key="minioadmin" --secret_key="minioadmin"

# update the store name against the stack
zenml stack update ml004_stack -a minio_store 
```

## Useful Zenml Commands

```bash
zenml stack set default
zenml experiment-tracker delete ml004_tracker
zenml model-deployer delete ml004_model
zenml stack delete -y ml004_stack

zenml artifact-store delete minio_store

zenml stack describe

# Display running models on ZENML
zenml model-deployer models list
zenml model-deployer models start  <uuid>
zenml model-deployer models delete  <uuid>
zenml model-deployer models describe   <uuid>

```
