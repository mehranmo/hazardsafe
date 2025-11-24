import time
import json
from src.integrations.langflow_components import (
    ComplianceAgentComponent, 
    ProvenanceAgentComponent, 
    ReportAgentComponent, 
    WorkflowManagerComponent
)

def interactive_hitl_demo():
    print("\n🤖 --- HazardSAFE Human-in-the-Loop (HITL) Demo --- 🤖\n")
    
    # 1. Setup
    wf_comp = WorkflowManagerComponent()
    scenario_id = "SCN-HITL-001"
    print(f"🔹 Initializing Workflow for {scenario_id}...")
    wf_id = wf_comp.build(action="Create", scenario_id=scenario_id)
    
    # 2. Input
    scenario = {
        "id": scenario_id,
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 25.0,
        "transport_index": 0.5
    }
    print(f"📄 Scenario Data:\n{json.dumps(scenario, indent=2)}\n")
    
    # 3. AI Analysis
    print("🕵️  Compliance Agent is analyzing...")
    time.sleep(1)
    comp_agent = ComplianceAgentComponent()
    # Using gemini-2.0-flash-exp (or mock if key missing)
    decision = comp_agent.build(scenario=scenario, model_name="gemini-2.0-flash-exp")
    
    print(f"\n💡 AI Recommendation: {'✅ APPROVE' if decision['compliant'] else '❌ REJECT'}")
    print(f"   Reason: {decision['reason']}\n")
    
    # 4. HITL Step
    print("🛑 [HITL TRIGGER] Human Review Required")
    user_input = input("👉 Do you authorize this decision? (y/n): ").strip().lower()
    
    if user_input == 'y':
        print("\n👤 Human Action: APPROVED")
        final_status = "APPROVED"
        
        # 5. Execution (Provenance + VC)
        print("📝 Logging to Provenance Ledger...")
        prov_agent = ProvenanceAgentComponent()
        log_result = prov_agent.build(
            agent_id="ComplianceAgent", 
            event_type="DECISION_MADE", 
            payload=decision
        )
        evidence_id = log_result['doc_id']
        
        if decision['compliant']:
            print("🏆 Issuing Verifiable Credential...")
            report_agent = ReportAgentComponent()
            vc = report_agent.build(
                scenario_id=scenario_id, 
                decision=decision, 
                evidence_id=evidence_id
            )
            print(f"   -> VC ID: {vc['id']}")
        
    else:
        print("\n👤 Human Action: REJECTED")
        final_status = "REJECTED"
        print("🚫 Workflow stopped. No VC issued.")

    # 6. Update State
    wf_comp.build(action="Update", doc_id=wf_id, status=final_status)
    print(f"\n✅ Workflow Final State: {final_status}")

if __name__ == "__main__":
    interactive_hitl_demo()
