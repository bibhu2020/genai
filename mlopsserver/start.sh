## Start script for the MLOps server
#!/bin/bash
# Start the MLOps server with Docker Compose
# set -e  

. ./env.sh || echo "⚠ env.sh failed, continuing..." # Load environment variables from .env file

docker compose up -d
# Wait for the services to be up and running
echo "Waiting for services to start..."
sleep 10  # Adjust the sleep time as necessary  
# Check if MinIO is running
if curl -s http://localhost:$MINIO_PORT/minio/health/live > /dev/null; then
    echo "MinIO is running on port $MINIO_PORT"
else
    echo "MinIO failed to start on port $MINIO_PORT"
    # exit 1
fi
# Check if MLflow is running
if curl -s http://localhost:$MLFLOW_PORT/ > /dev/null; then
    echo "MLflow is running on port $MLFLOW_PORT"
else
    echo "MLflow failed to start on port $MLFLOW_PORT"
    # exit 1
fi
# Check if ZenML is running
sleep 10
if curl -s http://localhost:$ZENML_PORT/ > /dev/null; then
    echo "ZenML is running on port $ZENML_PORT"
else
    echo "ZenML failed to start on port $ZENML_PORT"
    # exit 1
fi
echo "All services are up and running!" 
