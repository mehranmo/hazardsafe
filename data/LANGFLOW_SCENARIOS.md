# LangFlow Ready-to-Use Scenarios

## Quick Start: Copy & Paste into LangFlow

When building your flow in LangFlow, you'll need to input HazMat scenarios. Here are ready-to-use JSON snippets:

---

## Scenario 1: Normal Compliant Transport ✅
**Copy this into the Chat Input node:**

```json
{"id": "SCN-DEMO-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}
```

**Expected Result:** Compliant (Temperature is safe at 25°C)

---

## Scenario 2: High Temperature Violation ❌
**Copy this into the Chat Input node:**

```json
{"id": "SCN-DEMO-002", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 45.0, "transport_index": 0.5}
```

**Expected Result:** Non-compliant (Temperature exceeds 38°C limit)

---

## Scenario 3: Edge Case - Exactly at Limit ⚠️
**Copy this into the Chat Input node:**

```json
{"id": "SCN-EDGE-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 38.0, "transport_index": 0.5}
```

**Expected Result:** Compliant (Exactly at the 38°C threshold)

---

## How to Use in LangFlow:

1. **Open LangFlow**: `http://localhost:7860`

2. **Create Your Flow**:
   - Add a **Chat Input** node
   - Connect it to **Compliance Agent** (from HazardSAFE category)
   - Add another **Chat Input** for HITL approval
   - Connect to **Provenance Agent** → **Report Agent** → **Chat Output**

3. **Paste Scenario**:
   - Click on the first Chat Input node
   - In the "Message" field, paste one of the JSON scenarios above
   
4. **Run the Flow**:
   - Click "Run" button
   - The flow will analyze the scenario
   - At the HITL step, you decide (type "yes" or "no")
   - See the final VC if approved!

---

## For Automated Testing:

Use the full test suite:
```bash
PYTHONPATH=. python3 scripts/test_scenarios.py
```

This runs all 6 scenarios automatically with detailed reporting.
