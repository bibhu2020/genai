# Overview
This folder is where I've experimented out with traditional machine learning using **mlflow**. I've tested out what I've learned about machine learning from Edureka. 

My edureka notebooks are here: In my Personal Azure DevOps

## Create Project
```
uv init 
```

## Create a virtual environment
uv is like npm in nodejs. uv is created using RUST language.
```
uv python list

uv python install cpython-3.11.12-linux-x86_64-gnu 

uv venv _venv --python=cpython-3.11.12-linux-x86_64-gnu

source _venv/bin/activate

deactivate
```
## Install the packages
```
uv pip install -r requirements.txt

uv pip list
```

## Run the app
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

streamlit run streamlit_app.py
```
