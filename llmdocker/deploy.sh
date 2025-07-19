#!/bin/bash

# Check if a tag was passed as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <docker-tag>"
  exit 1
fi

# build the docker image
# 
# docker build -t ollama-model .

# docker run -d -p 11434:11434 --name ollama-container ollama-model


# login to ACR
az acr login --name aksocpocacr

kubectl config use-context aksoc-poc-eastus

kubectl config set-context --current --namespace=riskiq

# Set variables
DOCKER_TAG=$1
REGISTRY="aksocpocacr.azurecr.io"
K8S_DEPLOYMENT_FILE="./deployment.yaml"

# upload the image to docker
APP_NAME="ollama-gemma2b"
CODE_PATH="."
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/Dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

kubectl apply -f deployment.yaml

kubectl rollout restart deployment ollama-gemma2b