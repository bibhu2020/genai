#!/bin/bash

# Set variables
THRESHOLD=80   # % disk usage threshold
TARGET_DIRS=(
  "$HOME/actions-runner/_work"
  "$HOME/actions-runner/_diag"
  "$HOME/actions-runner/_temp"
)

# Get root filesystem disk usage
USAGE=$(df --output=pcent / | tail -1 | tr -dc '0-9')

if [ "$USAGE" -ge "$THRESHOLD" ]; then
  echo "[INFO] Disk usage is at ${USAGE}%, cleaning folders..."
  for dir in "${TARGET_DIRS[@]}"; do
    if [ -d "$dir" ]; then
      echo " - Deleting contents of $dir"
      rm -rf "${dir:?}/"*
    fi
  done
else
  echo "[INFO] Disk usage is at ${USAGE}%, no cleanup needed."
fi
