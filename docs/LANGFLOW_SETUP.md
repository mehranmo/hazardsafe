# HazardSAFE: LangFlow UI Setup Guide

To test the visual UI and orchestration, you can use **LangFlow**.

## 1. Installation
Install LangFlow in your environment:
```bash
pip install langflow
```

## 2. Running LangFlow
Start the UI server:
```bash
python -m langflow run
```
This will open the UI at `http://localhost:7860`.

## 3. Importing HazardSAFE Components
Since we have created custom Python components in `src/integrations/langflow_components.py`, you can import them into LangFlow.

1.  In the LangFlow UI, look for **"Custom Component"** in the sidebar.
2.  Drag a **Custom Component** node onto the canvas.
3.  Click the **"Code"** icon on the node.
4.  Copy and paste the code from `src/integrations/langflow_components.py` into the editor.
    *   *Note: You may need to paste each class (ComplianceAgentComponent, etc.) into separate Custom Component nodes.*
5.  Save the component.

## 4. Building the Flow
Connect the nodes in this order:
1.  **Workflow Manager** (Create)
2.  **Compliance Agent**
3.  **Provenance Agent**
4.  **Report Agent** (Conditional on compliance)
5.  **Workflow Manager** (Update)

## 5. Human-in-the-Loop (HITL)
To add the HITL step in LangFlow:
1.  Add a **"Chat Input"** or **"Prompt"** node between the Compliance Agent and the Provenance Agent.
2.  This effectively pauses the flow until a user provides input (e.g., "approve").
