# How to Import the HazardSAFE HITL Template into LangFlow

## Step 1: Start LangFlow
If not already running:
```bash
./run_demo.sh
# Select option 4
```

Or directly:
```bash
PYTHONPATH=. python3 -m langflow run
```

Access at: `http://localhost:7860`

## Step 2: Import the Template

1. **Open LangFlow UI** in your browser
2. Click **"New Flow"** or **"Import"** button
3. Navigate to: `langflow_templates/hazardsafe_hitl_flow.json`
4. Click **"Import"**

## Step 3: The Flow Structure

The imported flow will show:

```
[Scenario Input] → [Compliance Agent] → [HITL Approval] → [Provenance Agent] → [Report Agent] → [Output]
                           ↓                    ↓
                    [Workflow Init]      (Human Review)
```

### Components:

1. **Scenario Input**: Enter HazMat scenario JSON
2. **Compliance Agent**: AI analyzes compliance (RAG + Code-as-Policy)
3. **HITL Approval**: 🛑 **YOU decide** - Approve or Reject
4. **Provenance Agent**: Logs decision to immutable ledger
5. **Report Agent**: Issues Verifiable Credential (if approved)

## Step 4: Run the Flow

1. **Fill in Scenario**: Click "Scenario Input" and paste:
   ```json
   {
     "id": "SCN-TEST-001",
     "material_class": "Class 7",
     "package_type": "Type B(U)",
     "ambient_temperature_c": 25.0,
     "transport_index": 0.5
   }
   ```

2. **Click "Run"**: The flow executes

3. **HITL Pause**: When it reaches the "HITL Approval" node:
   - You'll see the AI's recommendation
   - Type `yes` to approve or `no` to reject

4. **View Results**: The final output shows:
   - Provenance event ID
   - Verifiable Credential (if approved)
   - Workflow status

## Troubleshooting

**If components don't load:**
- Ensure `PYTHONPATH=.` is set in your environment
- Restart LangFlow from the project root directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Missing modules:**
- The custom components import from `src/` directory
- Run LangFlow from `/home/mmonavar/Projects/aqi/aqi/` (project root)
