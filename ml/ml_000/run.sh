#!/bin/bash

# Exit immediately if any command fails
set -e

# Step 1: Build the Python package
python -m build

# Step 2: Move into the dist directory
cd dist

# Step 3: Install the built wheel package with force reinstall
uv pip install ml_000-0.1-py3-none-any.whl --force-reinstall

# Step 4: Move back to the original directory
cd ../..
