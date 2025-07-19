#!/bin/bash
set -e

# Just set permissions (directory already exists)
# chmod -R 777 /mlflow_artifacts
# chmod -R 777 /mlflow


exec "$@"
