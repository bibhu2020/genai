Project Reference:
https://www.youtube.com/watch?v=o6vbe5G7xNo

## Installing Python
sudo apt update
sudo apt install python3 python3-pip ipython3
sudo apt install python-is-python3
sudo apt install python3.10-venv

## Install uv
curl -Ls https://astral.sh/uv/install.sh | bash

## Installing Python
cd /home/azureuser/ws/genai/ml/ml_003
python -m venv .venv
source .venv/bin/activate
uv pip install -r ../requirements.txt

## Setup local Zenml server (not necessary since I've zenml running in docker locally - look at mlflowserver folder)
```
zenml init

zenml up

zenml down

zenml clean --yes

rm -rf ~/.config/zenml

zenml logout   # optional


# You can connect to it using the 'default' username and an empty password.
```


## zenml and mlflow integration
- zenml is used for ml pipeline (to execute learning and evaluation steps)

- mlflow is used to track evalution, metrix and metrics artifacts

- hence, both tool must be integrated.

``` bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python

```
```bash
zenml connect --url=http://localhost:8237 --username=admin --password=Zenml@123

zenml integration install mlflow #--uv -y


# activate mlflow tracker 
zenml experiment-tracker register mlflow_tracker \
    --flavor=mlflow \
    --tracking_uri=http://localhost:5000 \
    --tracking_username=none \
    --tracking_password=none # or localhost if outside Docker

#zenml stack update <stack-name> --experiment-tracker mlflow_tracker

zenml stack copy default mlflow-stack


zenml stack update mlflow-stack -e mlflow_tracker

# activate the stack
zenml stack set mlflow-stack

```

# delete a stack and tracker (by creating a temp one)
```
zenml experiment-tracker register temp_tracker1 --flavor=mlflow
zenml stack update mlflow-stack -e temp_tracker1
zenml experiment-tracker delete mlflow_tracker
zenml stack delete mlflow-stack
zenml experiment-tracker delete temp_tracker1

```