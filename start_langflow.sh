#!/bin/bash
# Comprehensive LangFlow startup script with all required settings

cd /home/mmonavar/Projects/aqi/aqi

export PYTHONPATH=/home/mmonavar/Projects/aqi/aqi
export LANGFLOW_COMPONENTS_PATH=/home/mmonavar/Projects/aqi/aqi/components
export LANGFLOW_SKIP_AUTH_AUTO_LOGIN=true

echo "🚀 Starting LangFlow with HazardSAFE components..."
echo "   Components path: $LANGFLOW_COMPONENTS_PATH"
echo "   Python path: $PYTHONPATH"
echo ""

python3 -m langflow run --host 0.0.0.0 --port 7860
