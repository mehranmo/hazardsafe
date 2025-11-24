# Import HazardSAFE Template into LangFlow

## Quick Import (2 Steps)

### Step 1: Open LangFlow
Navigate to: `http://localhost:7860`

### Step 2: Import the Template
1. Click the **"Import"** or **"📥"** button in the top menu
2. Browse to: `langflow_templates/hazardsafe_working_export.json`
3. Click "Open"

**✅ Done!** The flow will open with the scenario already pre-loaded.

---

## What's Included in the Template

The template contains a complete HITL workflow:

**Nodes:**
1. **Chat Input (Scenario)** - Pre-loaded with test scenario
2. **Compliance Agent** - Checks HazMat regulations
3. **Chat Input (HITL)** - Human approval point
4. **Provenance Agent** - Logs decisions
5. **Report Agent** - Issues Verifiable Credentials
6. **Chat Output** - Shows final result

**Pre-loaded Scenario:**
```json
{"id": "SCN-DEMO-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}
```

---

## How to Use After Import

1. **Review the Flow**: Nodes should be connected automatically
2. **Click "Run"**: Start the workflow
3. **HITL Step**: When prompted, type "yes" or "no"
4. **See Results**: VC is issued if approved

---

## Alternative Test Scenarios

Replace the scenario in the first Chat Input with these:

**High Temperature (Should Fail)**:
```json
{"id": "SCN-002", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 45.0, "transport_index": 0.5}
```

**Edge Case (Exactly at limit)**:
```json
{"id": "SCN-003", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 38.0, "transport_index": 0.5}
```

---

## Troubleshooting

### ❌ Import Fails or Components Missing?

**Ensure LangFlow is running with custom components:**
```bash
./start_langflow.sh
```

This sets `LANGFLOW_COMPONENTS_PATH` so HazardSAFE components load.

### ✅ Verify Components Loaded:
Components from "HazardSAFE" category should appear in the sidebar.

---

## File Location

**Template File**: `langflow_templates/hazardsafe_working_export.json`

This is a direct export from the working flow created via API, ensuring compatibility.

---

**🎉 Enjoy your ready-to-use HITL workflow!**
