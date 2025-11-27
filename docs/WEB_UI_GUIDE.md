# HazardSAFE Web UI Guide (Streamlit)

## Overview

The HazardSAFE Web UI has been upgraded to a modern **Streamlit** application. It provides a premium, responsive interface for human reviewers to approve or reject workflows, generate tests, and audit history.

## Quick Start

### 1. Start the Web UI

```bash
# From project root
./scripts/start_web_ui.sh
```

The UI will be available at: **http://localhost:5000**

### 2. Run a Demo Workflow

You can now generate workflows directly from the UI!
Go to the **🧪 Test Generator** tab and click **Generate Scenario**.

Or use the CLI:
```bash
PYTHONPATH=. python3 scripts/create_test_workflow.py
```

## Features

### 1. 📋 Pending Approvals
- **Card View**: Modern card layout for each pending workflow.
- **AI Insight**: Clear display of AI compliance decision and reasoning.
- **Actions**: Approve or Reject with comments.
- **Real-time**: Updates automatically after action.

### 2. 🧪 Test Generator
- **Instant Scenarios**: Generate Pass, Fail, or Edge case scenarios with one click.
- **Live Feedback**: See the generated data and AI decision immediately.

### 3. 🏗️ Architecture
- **Visual Diagram**: Interactive graph showing the state machine (Draft → Pending → Approved/Rejected).
- **Agent Roles**: Clear table explaining what each agent does.

### 4. 📜 History & Audit
- **Data Grid**: Sortable, filterable table of all past workflows.
- **Deep Dive**: Select any workflow to see full JSON metadata and state transition history.
- **Color Coded**: Statuses are visually distinct (Green=Approved, Red=Rejected, Orange=Pending).

## Configuration

Edit `config/hitl_config.yaml`:

```yaml
timeout_hours: 24
auto_reject_on_timeout: true
web_ui:
  port: 5000
```

## Troubleshooting

### Web UI won't start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Fix**:
```bash
pip install streamlit graphviz pandas
```

### Graphviz Error
If the architecture diagram doesn't show, you might need system-level graphviz:
```bash
sudo apt-get install graphviz  # Linux
brew install graphviz          # Mac
```
*(Note: The Python library usually works without this for simple diagrams, but good to know)*

---

**🎉 Enjoy the new Streamlit UI!**
