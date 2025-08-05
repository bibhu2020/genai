#!/bin/bash
# Start the MLOps server with Docker Compose
set -e  

. ./env.sh  # Load environment variables from .env file

docker compose down
