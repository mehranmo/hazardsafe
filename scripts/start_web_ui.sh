#!/bin/bash
# Startup script for HazardSAFE HITL Web UI (Streamlit)

echo "========================================"
echo "  Starting HazardSAFE HITL Web UI"
echo "========================================"

# Set PYTHONPATH to include project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if config exists
if [ ! -f "config/hitl_config.yaml" ]; then
    echo "⚠️  Warning: config/hitl_config.yaml not found"
    echo "   Using default configuration"
fi

# Install dependencies if needed (quick check)
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Installing Streamlit..."
    pip install streamlit graphviz pandas
fi

# Start the Streamlit app
# --server.port 5000 to match previous config
# --server.address 0.0.0.0 to allow external access
python3 -m streamlit run src/web/streamlit_app.py --server.port 5000 --server.address 0.0.0.0
