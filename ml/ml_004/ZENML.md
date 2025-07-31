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

## Connect your app to zenml server (from CLI)
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
zenml experiment-tracker register ml004_tracker --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" 
#Step3: Registers a model deployer component (name: ml004_model). --flavor=mlflow tells the backend mlflow
zenml model-deployer register ml004_model --flavor=mlflow --tracking_uri=http://localhost:5000  --tracking_token="dummy_token" 
#Step4: Registers a full ZenML stack — a combination of components like orchestrator, artifact store, experiment tracker, etc. 
## -a default: Sets the artifact store to the default (often local).
## -o default: Sets the orchestrator to the default (e.g., local or airflow).
## -d ml004_model: Uses the model deployer named ml004_model (registered in step 3).
## -e ml004_tracker: Uses the experiment tracker named ml004_tracker (from step 2).
## --set: Sets this stack as the active stack for future runs.
zenml stack register ml004_stack -a default -o default -d ml004_model -e ml004_tracker --set
```

## Connect to Zenml from CI/CD pipelines
From you local development machine connect to zenml and link zenml to mlflow. Also define the tracker and stack.
This stores the stack and project id in the .zen folder. Hence, this is crucial to be checked into git.

From you development machine (after loging in to Zenml), create a service account. this geneates an API_KEY
zenml service-account create <SERVICE_ACCOUNT_NAME>


```bash
# In pipeline set the following 2 environment variable to login to zenml no interactively.
export ZENML_STORE_URL=https://...
export ZENML_STORE_API_KEY=<API_KEY>

```
- No need for zenml login from the pipeline. the above environment variable takes care

- No need for zenml init since .zen folder is part of the code.

- No need for defining stack since code includes the .zen folder.



## Delete a stack from zenml
```bash
zenml stack set default
zenml experiment-tracker delete ml004_tracker
zenml model-deployer delete ml004_model
zenml stack delete -y ml004_stack
```