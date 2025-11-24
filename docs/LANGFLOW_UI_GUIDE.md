# LangFlow UI Setup Guide - HazardSAFE HITL Workflow

## Status ✅

**Components**: ✅ Loaded and working  
**LangFlow**: ✅ Running at http://localhost:7860  
**Issue**: API-created flows appear empty in UI  
**Solution**: Manual flow creation (standard LangFlow workflow)

## Quick Start: Build the Flow Manually

LangFlow is designed for visual, drag-and-drop flow creation. Here's how to build your HITL workflow:

### Step 1: Open LangFlow
1. Navigate to: `http://localhost:7860`
2. You should see the flows list page

### Step 2: Create a New Flow
1. Click the **"+ New Flow"** button  
2. You'll see an empty canvas with a components sidebar on the left

### Step 3: Check for HazardSAFE Components
**⚠️ Important**: If you DON'T see a "HazardSAFE" category in the sidebar:
- The custom components path may not be loaded
- Restart LangFlow using: `./start_langflow.sh`
- This ensures `LANGFLOW_COMPONENTS_PATH` is properly set

### Step 4: Build the Workflow
Drag components onto the canvas in this order:

#### A. Input Node
- Search for **"Chat Input"** in the sidebar
- Drag it to the canvas
- In its settings, paste this scenario:
```json
{"id": "SCN-DEMO-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}
```

#### B. Compliance Agent
- Find **"Compliance Agent"** under "HazardSAFE" category  
- Drag it to the canvas (to the right of Chat Input)
- Connect: Chat Input → Compliance Agent

#### C. HITL Approval (Another Chat Input)
- Add another **"Chat Input"** node
- Label it: "HITL Approval"
- This is where you'll type "yes" or "no"

#### D. Provenance Agent
- Find **"Provenance Agent"** under "HazardSAFE"
- Drag it next
- Connect: Compliance Agent → Provenance Agent

#### E. Report Agent
- Find **"Report Agent"** under "HazardSAFE"
- Drag it next
- Connect: Provenance Agent → Report Agent

#### F. Output Node
- Search for **"Chat Output"**
- Drag it to the end
- Connect: Report Agent → Chat Output

### Step 5: Run the Workflow
1. Click the **"Run"** or **"Play"** button
2. The scenario will be checked
3. You'll be prompted for approval (HITL step)
4. Type "yes" to approve
5. See the Verifiable Credential output!

## Troubleshooting

###  Components Not Visible?
**Symptoms**: No "HazardSAFE" category in sidebar

**Fix**:
```bash
# Kill current LangFlow
pkill -f "langflow run"

#Start with proper settings
./start_langflow.sh
```

**Verify**: Run this to confirm components load:
```bash
python3 -c "import sys; sys.path.insert(0, './components'); from hazardsafe.compliance_agent import ComplianceAgentComponent; print(f'✅ {ComplianceAgentComponent.display_name}')"
```

###  Empty Flow When Clicking API-Created Flows?
**This is expected!** API-created flows don't render properly in Lang Flow's UI.

**Solution**: Ignore the API-created flows and build manually using drag-and-drop (see steps above).

### Alternative: Use Python CLI Demo
If the UI continues to have issues, use the fully-functional Python version:
```bash
PYTHONPATH=. python3 scripts/hitl_demo.py
```

This provides the same HITL workflow without needing the UI.

## Why Manual is Better

1. **Visual Feedback**: See the flow as you build it
2. **Immediate Testing**: Run and debug each node
3. **Native LangFlow**: Uses the tool as intended
4. **Flexible**: Easy to modify and experiment

## Pre-loaded Scenarios

Copy-paste these into the first Chat Input node:

**Scenario 1 - Pass**:
```json
{"id": "SCN-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}
```

**Scenario 2 - Fail (High Temp)**:
```json
{"id": "SCN-002", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 45.0, "transport_index": 0.5}
```

**Scenario 3 - Edge Case**:
```json
{"id": "SCN-003", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 38.0, "transport_index": 0.5}
```

---

**🎉 You're Ready!** Open http://localhost:7860 and start building!
