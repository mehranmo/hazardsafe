# HazardSAFE: Agentic Quality Infrastructure for HazMat Safety
# ============================================================
# This script demonstrates the end-to-end flow of the HazardSAFE system.
# It simulates the "LangFlow" visual orchestration pipeline programmatically.

import os
import json
import time
from src.integrations.langflow_components import (
    ComplianceAgentComponent, 
    ProvenanceAgentComponent, 
    ReportAgentComponent, 
    WorkflowManagerComponent
)

# Ensure API Key is present (or Mock Mode will trigger)
if "GOOGLE_API_KEY" not in os.environ:
    print("ℹ️  GOOGLE_API_KEY not found. System will run in MOCK MODE.")

def run_demo():
    print("\n🚀 Starting HazardSAFE Demo Workflow...\n")
    
    # 1. Initialize Workflow
    print("1️⃣  Workflow Manager: Initializing Assessment...")
    wf_comp = WorkflowManagerComponent()
    scenario_id = "SCN-DEMO-2025"
    wf_id = wf_comp.build(action="Create", scenario_id=scenario_id)
    print(f"   -> Workflow Created: {wf_id}")
    time.sleep(1)

    # 2. Define Scenario (Input)
    scenario = {
        "id": scenario_id,
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 25.0, # Safe (Limit is 38.0)
        "transport_index": 0.5
    }
    print(f"\n📄 Input Scenario: {json.dumps(scenario, indent=2)}")

    # 3. Compliance Check (Agent 1)
    print("\n2️⃣  Compliance Agent: Checking Regulations...")
    comp_agent = ComplianceAgentComponent()
    # We use the 'gemini-2.0-flash-exp' model
    decision = comp_agent.build(scenario=scenario, model_name="gemini-2.0-flash-exp")
    
    print(f"   -> Decision: {'✅ Compliant' if decision['compliant'] else '❌ Non-Compliant'}")
    print(f"   -> Reason: {decision['reason']}")
    time.sleep(1)

    # 4. Provenance Logging (Agent 2)
    print("\n3️⃣  Provenance Agent: Logging Event...")
    prov_agent = ProvenanceAgentComponent()
    log_result = prov_agent.build(
        agent_id="ComplianceAgent", 
        event_type="DECISION_MADE", 
        payload=decision
    )
    evidence_id = log_result['doc_id']
    print(f"   -> Event Logged to Immutable Ledger. ID: {evidence_id}")
    time.sleep(1)
    
    # 4. Report & VC Issuance (Agent 3)
    if decision['compliant']:
        print("\n4️⃣  Report Agent: Issuing Verifiable Credential...")
        report_agent = ReportAgentComponent()
        vc = report_agent.build(
            scenario_id=scenario_id, 
            decision=decision, 
            evidence_id=evidence_id
        )
        print(f"   -> 🏆 VC Issued: {vc['id']}")
        print(f"   -> Issuer: {vc['issuer']}")
        
        # Update workflow: Trigger HITL then auto-approve for demo
        print("\n5️⃣  Workflow: Auto-approving (demo mode)...")
        # First transition to PENDING_HITL
        wf_comp.build(action="Update", doc_id=wf_id, status="PENDING_HITL", 
                     metadata={"decision_data": decision, "hitl_triggered_at": int(time.time())})
        # Then approve (simulating human approval)
        wf_comp.build(action="Update", doc_id=wf_id, status="APPROVED",
                     metadata={"human_reviewer": "demo-auto-approver", "human_comments": "Auto-approved in demo mode"})
        print("\n✅ Workflow Status: APPROVED")
        
    else:
        print("\n4️⃣  Report Agent: Skipping VC (Non-Compliant).")
        # Trigger HITL then auto-reject
        wf_comp.build(action="Update", doc_id=wf_id, status="PENDING_HITL",
                     metadata={"decision_data": decision, "hitl_triggered_at": int(time.time())})
        wf_comp.build(action="Update", doc_id=wf_id, status="REJECTED",
                     metadata={"human_reviewer": "demo-auto-approver", "human_comments": "Auto-rejected in demo mode"})
        print("\n⛔ Workflow Status: REJECTED")

    print("\n✨ Demo Complete!")

if __name__ == "__main__":
    run_demo()
