#!/bin/bash
# HazardSAFE Demo Launcher

export PYTHONPATH=.

echo "=== HazardSAFE Demo Menu ==="
echo "1. Run End-to-End Demo"
echo "2. Run HITL Interactive Demo"
echo "3. Run Adversarial Evaluation"
echo "4. Start LangFlow UI"
echo ""
read -p "Select option (1-4): " choice

case $choice in
  1)
    echo "Running End-to-End Demo..."
    python3 notebook.py
    ;;
  2)
    echo "Running HITL Demo..."
    python3 scripts/hitl_demo.py
    ;;
  3)
    echo "Running Adversarial Evaluation..."
    python3 src/eval/evaluate.py
    ;;
  4)
    echo "Starting LangFlow UI..."
    echo "LangFlow will be available at http://localhost:7860"
    export LANGFLOW_COMPONENTS_PATH=/home/mmonavar/Projects/aqi/aqi/components
    export LANGFLOW_SKIP_AUTH_AUTO_LOGIN=true
    python3 -m langflow run --host 0.0.0.0 --port 7860
    ;;
  *)
    echo "Invalid option"
    ;;
esac
