#!/bin/bash

set -e  # Exit on any error

# Source environment variables from ../../mlopsserver/env.sh
if [ -f "../../mlopsserver/env.sh" ]; then
  echo "Sourcing environment variables from ../../mlopsserver/env.sh"
  source ../../mlopsserver/env.sh
else
  echo "Warning: ../../mlopsserver/env.sh not found. Continuing without sourcing env vars."
fi

# Get current folder name and remove underscores
PREFIX=$(basename "$PWD")
PREFIX=${PREFIX//_/}  # Remove all underscores

echo "Using prefix: $PREFIX"

# Create conda env only if it doesn't exist
if [ ! -d "./.venv" ]; then
  echo "Creating conda env in ./.venv"
  conda create --prefix ./.venv python=3.11 -y
else
  echo "Conda env already exists at ./.venv"
fi

# Activate conda env
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ./.venv

# Install requirements (pip install is safe to run multiple times)
echo "Installing requirements"
uv pip install -r requirements.txt

# Initialize zenml project only if not initialized
if [ ! -d ".zen" ]; then
  echo "Initializing ZenML"
  zenml init
  zenml project set default
else
  echo "ZenML already initialized"
fi

# Install mlflow integration if not installed
if ! zenml integration list | grep -q "mlflow"; then
  echo "Installing mlflow integration"
  zenml integration install mlflow -y
else
  echo "MLflow integration already installed"
fi

# Helper function to register resource only if not exists
function register_if_not_exists() {
  local type=$1
  local name=$2
  local cmd=$3

  if zenml $type describe "$name" > /dev/null 2>&1; then
    echo "$type '$name' already registered"
  else
    echo "Registering $type '$name'"
    eval "$cmd"
  fi
}


# Register experiment tracker
register_if_not_exists "experiment-tracker" "${PREFIX}_tracker" \
  "zenml experiment-tracker register ${PREFIX}_tracker --flavor=mlflow --tracking_uri=http://localhost:5000 --tracking_token='dummy_token'"

# Register model deployer
register_if_not_exists "model-deployer" "${PREFIX}_model" \
  "zenml model-deployer register ${PREFIX}_model --flavor=mlflow --tracking_uri=http://localhost:5000 --tracking_token='dummy_token'"

# Register stack (register or update)
if zenml stack describe "${PREFIX}_stack" > /dev/null 2>&1; then
  echo "Stack '${PREFIX}_stack' already registered. Updating stack components and setting active."
  zenml stack update ${PREFIX}_stack -a minio_store -o default -d ${PREFIX}_model -e ${PREFIX}_tracker
  zenml stack set ${PREFIX}_stack
else
  echo "Registering stack '${PREFIX}_stack'"
  zenml stack register ${PREFIX_}stack -a minio_store -o default -d ${PREFIX}_model -e ${PREFIX}_tracker --set
fi


echo "Setup complete with prefix: $PREFIX"
