#!/bin/bash
# Start the MLOps server with Docker Compose
# set -e  

. $HOME/ws/genai/mlopsserver/env.sh 

docker compose -f $HOME/ws/genai/mlopsserver/docker-compose.yaml  down
