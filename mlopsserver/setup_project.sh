#!/bin/bash
# Usage: ./setup_zenml_stack.sh <STACK_NAME> <MODEL_DEPLOYER_NAME> <TRACKER_NAME>

# set -euo pipefail

# Validate input arguments
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <STACK_NAME> <MODEL_DEPLOYER_NAME> <TRACKER_NAME>"
else
    STACK_NAME="$1"
    MODEL_NAME="$2"
    TRACKER_NAME="$3" 

    # Check if conda is installed
    if ! command -v conda &> /dev/null; then
        echo "❌ Conda is not installed. Please install Miniconda or Anaconda."
    else

        # Setup Conda environment
        echo "🔧 Setting up Conda environment..."
        uv init
        conda create --prefix ./.venv python=3.11 -y

        # Activate the environment
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate "$(pwd)/.venv"

        # Install dependencies
        echo "📦 Installing Python packages..."
        uv pip install -r requirements.txt
        uv pip install mlflow==2.15.1
        uv pip install 'zenml[server]==0.84.0'

        # Initialize ZenML
        echo "🚀 Initializing ZenML..."
        zenml login || true
        zenml init

        # Setup ZenML Stack
        echo "🔧 Installing mlflow integration..."
        zenml integration install mlflow -y

        echo "🧪 Registering experiment tracker: $TRACKER_NAME"
        zenml experiment-tracker register "$TRACKER_NAME" \
        --flavor=mlflow \
        --tracking_uri=http://localhost:5000 \
        --tracking_token="dummy_token"

        echo "📦 Registering model deployer: $MODEL_NAME"
        zenml model-deployer register "$MODEL_NAME" \
        --flavor=mlflow \
        --tracking_uri=http://localhost:5000 \
        --tracking_token="dummy_token"

        echo "🏗️  Registering stack: $STACK_NAME"
        zenml stack register "$STACK_NAME" \
        -a default -o default \
        -d "$MODEL_NAME" -e "$TRACKER_NAME" --set

        echo "🗃️  Updating artifact store to minio for stack: $STACK_NAME"
        zenml stack update "$STACK_NAME" -a minio_store

        echo "✅ ZenML stack '$STACK_NAME' set up successfully."
    fi

fi






