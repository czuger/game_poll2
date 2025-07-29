#!/bin/bash

# Check if parameter is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <base_directory>"
    exit 1
fi

BASE_DIR="$1"

# Check if directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Directory '$BASE_DIR' does not exist"
    exit 1
fi

# Change to the directory
cd "$BASE_DIR"

# Export the directory to PYTHONPATH
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"

# Run a simple Python script
python3 poll/scripts/compute_votes.py
