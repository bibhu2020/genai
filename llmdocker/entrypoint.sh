#!/bin/bash
# Start the Ollama server in the background
ollama serve  &

# Wait for it to be ready
until curl -s http://localhost:11434 > /dev/null; do
  echo "Waiting for Ollama to start..."
  sleep 1
done

# Pull the model
ollama pull gemma:2b

# Stay alive as a service
tail -f /dev/null