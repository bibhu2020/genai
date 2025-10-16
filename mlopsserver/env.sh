# # MinIO access keys - these are needed by MLflow
# export MINIO_ACCESS_KEY=XeAMQQjZY2pTcXWfxh4H
# export MINIO_SECRET_ACCESS_KEY=wyJ30G38aC2UcyaFjVj2dmXs1bITYkJBcx0FtljZ

# MinIO configuration
export MINIO_ROOT_USER='minioadmin'
export MINIO_ROOT_PASSWORD='minioadmin'
export MINIO_PORT=9000
export MINIO_CONSOLE_PORT=9001

# SQL SERVER
export MYSQL_ROOT_PASSWORD=password
export MYSQL_PORT=3306

# MLflow configuration
export MLFLOW_PORT=5000
export MLFLOW_BUCKET_NAME=mlflowartifacts
export MLFLOW_DB=mlflow_db
export MLFLOW_TRACKING_URI=http://localhost:5000

# ZENML configuration
export ZENML_PORT=8237
export ZENML_BUCKET_NAME=zenmlartifacts
export ZENML_DB=zenml
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:9000/
export ZENML_SERVER_JWT_SECRET_KEY="x09a@3sad*Df42ad566bb"
