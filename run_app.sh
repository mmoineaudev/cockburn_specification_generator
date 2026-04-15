#!/bin/bash

# Simple wrapper script to run the Cockburn Specification Generator

echo "Starting Cockburn Specification Generator V2..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found"
    exit 1
fi

# Check if PyQt6 is installed
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "Error: PyQt6 is not installed"
    echo "Please install with: pip install --break-system-packages PyQt6"
    exit 1
fi

# Run the application
python3 main.py