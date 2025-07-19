#!/bin/bash

# Check if a tag was passed as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <docker-tag>"
  exit 1
fi

# login to ACR and set the AKS context
az acr login --name aksocpocacr

kubectl config use-context aksoc-poc-eastus

kubectl config set-context --current --namespace=riskiq


# Set variables
DOCKER_TAG=$1
REGISTRY="aksocpocacr.azurecr.io"
K8S_DEPLOYMENT_FILE="./k8deployment.yaml"

# App1 (PORT 3001) (nestjs/northwind/apps/apigateway): A microservice gateway to all other services.
APP_NAME="apigateway-nestjs"
CODE_PATH="nestjs/northwind"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/dockers/${APP_NAME}-dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

# App2 (PORT 3002) (nestjs/northwind/apps/northwindapi): An API to server northwind postgress db from neon (https://neon.tech/). It demos nestjs way to define API using MVC framework.
APP_NAME="northwindapi-nestjs"
CODE_PATH="nestjs/northwind"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/dockers/${APP_NAME}-dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

# App3 (PORT 3003) (nestjs/northwind/apps/oauthapi): A nestjs app to demo oauth (this is recreation of the nodejs/oauthapi). 

# App4 (PORT 3004) (nestjs/northwind/apps/oauthapp): A nestjs app to demo oauth (this is recreation of the nodejs/oauthapp). It calls nodejs/oauthapi.
APP_NAME="oauthapp-nestjs"
CODE_PATH="nestjs/northwind"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/dockers/${APP_NAME}-dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}


# App5 (PORT 3005) (nestjs/northwind/apps/weatherapi): 
APP_NAME="weatherapi-nestjs"
CODE_PATH="nestjs/northwind"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/dockers/${APP_NAME}-dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

# App6 (PORT 3006) (nestjs/northwind/apps/azureapi): demonstrate websocket and event driven architecture. It is a stock price ticker app that uses websocket to push stock prices to the client. It is built using nestjs and rxjs.
APP_NAME="azureapi-nestjs"
CODE_PATH="nestjs/northwind"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/dockers/${APP_NAME}-dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

# App7 (PORT 3007) (nestjs/northwind/apps/stockapi): demonstrate websocket and event driven architecture. It is a stock price ticker app that uses websocket to push stock prices to the client. It is built using nestjs and rxjs.

# App8 (PORT 3011) (vuejs/northwind): A vuejs SPA northwind app. It is built to demo vuejs SPA.
APP_NAME="northwind-vuejs"
CODE_PATH="vuejs/northwind"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/Dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

# App9 (PORT 3012) (nodejs/oauthapp): A nodejs app built to demostrate azure security and oauth. It calls nodejs/oauthapi.

# App10 (PORT 3013) (nodejs/oauthapi): A nodejs app built to demostrate azure security and oauth. It calls nodejs/oauthapi.

# App11 (PORT 3021) (genai/mcp/mcp-server): A MCP server that is built to interact to Postregress DB. It is built to demo how to use mcp server to interact with postgress db. It is built using python.
APP_NAME="mcp-server"
CODE_PATH="genai/mcp/mcp-server"
DOCKER_IMAGE_NAME="${REGISTRY}/${APP_NAME}:${DOCKER_TAG}"
echo "Building Docker image..."
docker build -t ${APP_NAME} -f ${CODE_PATH}/Dockerfile ${CODE_PATH}/
echo "Tagging Docker image as ${DOCKER_IMAGE_NAME}..."
docker tag ${APP_NAME} ${DOCKER_IMAGE_NAME}
echo "Pushing Docker image to registry ${DOCKER_IMAGE_NAME}..."
docker push ${DOCKER_IMAGE_NAME}

# Deploy into AKS k8 (riskiq namespace)
echo "Deploying to Kubernetes using ${K8S_DEPLOYMENT_FILE}..."
kubectl apply -f ${K8S_DEPLOYMENT_FILE}

echo "Deployment complete!"

kubectl rollout restart deployment apigateway-nestjs
kubectl rollout restart deployment northwindapi-nestjs
kubectl rollout restart deployment oauthapp-nestjs
kubectl rollout restart deployment northwind-vuejs
kubectl rollout restart deployment azureapi-nestjs
kubectl rollout restart deployment weatherapi-nestjs
kubectl rollout restart deployment mcp-server



