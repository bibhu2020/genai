# Overview
This is an AI Agentic Trip Planner for planning a trip to any country worldwide with real-time data. It's going to have the 
following features:
- Real-time weather info
- Attraction and Activity List
- Hotel Costs
- Currency Conversion
- Itenary Planning
- Total Expenses
- Summerizer

## Create Project
```
uv init ai-trip-planner
```

## Create a virtual environment
uv is like npm in nodejs. uv is created using RUST language.
```
uv python list

uv python install cpython-3.11.12-linux-x86_64-gnu 

uv venv .venv --python=cpython-3.11.12-linux-x86_64-gnu

source .venv/bin/activate

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