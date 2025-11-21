#!/bin/bash
# install.sh — One-click Circle AI setup (for anyone)

set -e

echo "Circle AI — installing everything…"

# Create venv if it doesn't exist
[ ! -d "venv" ] && python3 -m venv venv --prompt CircleAI

# Activate venv
source venv/bin/activate

# Install exact dependencies
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Make launcher executable
chmod +x run.sh

echo ""
echo "===================================================="
echo "Circle AI is ready."
echo "Double-click run.sh or run: ./run.sh"
echo "Opens at → http://localhost:8501"
echo "===================================================="
