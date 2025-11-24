#!/usr/bin/env python3
"""
Script to demonstrate HazardSAFE in LangFlow UI.
This creates a step-by-step guide for the user.
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                  HazardSAFE LangFlow HITL Demo                       ║
╚══════════════════════════════════════════════════════════════════════╝

Custom components have been created in: components/hazardsafe/

LangFlow is starting with custom components loaded.

📍 STEP 1: Access LangFlow UI
   Open your browser: http://localhost:7860

📍 STEP 2: Create a New Flow
   - Click "+ New Flow" button
   - Name it "HazardSAFE HITL Workflow"

📍 STEP 3: Find HazardSAFE Components
   - Look in the left sidebar under "HazardSAFE" category
   - You should see:
     • Compliance Agent
     • Provenance Agent  
     • Report & VC Agent

📍 STEP 4: Build the HITL Flow
   Drag and connect components in this order:

   [Chat Input]
        ↓
   [Compliance Agent] ← Paste scenario JSON here
        ↓
   [Chat Input] ← HITL: You approve/reject here
        ↓
   [Provenance Agent]
        ↓  
   [Report & VC Agent]
        ↓
   [Chat Output]

📍 STEP 5: Configure Components
   - Chat Input 1 (Scenario): Set default value to:
     {"id": "SCN-001", "material_class": "Class 7", 
      "package_type": "Type B(U)", "ambient_temperature_c": 25.0}
   
   - Chat Input 2 (HITL): This is where YOU decide!
     Type "yes" to approve or "no" to reject

📍 STEP 6: Run the Flow
   - Click the "Run" button
   - The flow will pause at the HITL step
   - You make the decision!
   - See the VC issued if you approve

═══════════════════════════════════════════════════════════════════════

💡 TIP: You can also run pre-made demos:
   ./run_demo.sh  (choose option 1, 2, or 3)

🔗 LangFlow UI: http://localhost:7860

═══════════════════════════════════════════════════════════════════════
""")
