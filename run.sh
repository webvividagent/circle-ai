#!/bin/bash
# run.sh — Circle AI launcher (final – works forever)

cd "$(dirname "$0")"

# Activate the venv that install.sh created
source venv/bin/activate

echo "===================================================="
echo "Circle AI — Neural Mapping • The Five Agents"
echo "→ http://localhost:8501"
echo "Close window or Ctrl+C to stop"
echo "===================================================="

# Launch using the venv's python (guaranteed to have streamlit)
exec python -m streamlit run ecl_temple.py \
  --server.runOnSave true \
  --server.port 8501 \
  --theme.base dark
