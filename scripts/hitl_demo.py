import time
import json
from src.integrations.langflow_components import (
    ComplianceAgentComponent, 
    ProvenanceAgentComponent, 
    ReportAgentComponent
)
from src.workflow.manager import WorkflowManager

def interactive_hitl_demo():
    print("\n🤖 --- HazardSAFE Human-in-the-Loop (HITL) Demo --- 🤖\n")
    
    # Initialize managers
    wf_manager = WorkflowManager()
    scenario_id = "SCN-HITL-001"
    
    # Define scenario
    scenario = {
        "id": scenario_id,
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 25.0,
        "transport_index": 0.5
    }
    
    print(f"🔹 Creating workflow for {scenario_id}...")
    wf_id = wf_manager.create_workflow(scenario_id, scenario_data=scenario)
    print(f"📄 Scenario Data:\n{json.dumps(scenario, indent=2)}\n")
    
    # AI Analysis
    print("🕵️  Compliance Agent is analyzing...")
    time.sleep(1)
    comp_agent = ComplianceAgentComponent()
    decision = comp_agent.build(scenario=scenario, model_name="gemini-2.0-flash-exp")
    
    print(f"\n💡 AI Recommendation: {'✅ APPROVE' if decision['compliant'] else '❌ REJECT'}")
    print(f"   Reason: {decision['reason']}\n")
    
    # Trigger HITL
    print("🛑 [HITL TRIGGER] Transitioning to PENDING_HITL state...")
    wf_manager.trigger_hitl(wf_id, decision)
    
    # Log HITL trigger to provenance
    prov_agent = ProvenanceAgentComponent()
    prov_agent.build(
        agent_id="WorkflowManager",
        event_type="HITL_TRIGGERED",
        payload={
            "workflow_id": wf_id,
            "scenario_id": scenario_id,
            "decision_data": decision
        }
    )
    
    print(f"\n{'='*60}")
    print(f"  Workflow ID: {wf_id}")
    print(f"  Status: PENDING_HITL")
    print(f"{'='*60}")
    print(f"\n📋 Next Steps:")
    print(f"  1. Open the Web UI: http://localhost:5000")
    print(f"  2. Review the scenario and AI recommendation")
    print(f"  3. Approve or Reject the workflow")
    print(f"\n  OR continue with CLI approval below:")
    print(f"{'='*60}\n")
    
    # CLI Option
    user_input = input("👉 Approve this workflow? (y/n/skip): ").strip().lower()
    
    if user_input == 'skip':
        print("\n⏸️  Workflow paused. Use Web UI to complete approval.")
        print(f"   Workflow ID: {wf_id}")
        return
    
    if user_input == 'y':
        user_id = input("👉 Your ID/Email: ").strip() or "cli-user@hazardsafe.ai"
        comments = input("👉 Comments (optional): ").strip()
        
        print(f"\n👤 Approving as {user_id}...")
        wf_manager.approve_workflow(wf_id, user_id, comments)
        
        # Log approval to provenance
        prov_agent.build(
            agent_id="CLI",
            event_type="HITL_APPROVED",
            payload={
                "workflow_id": wf_id,
                "scenario_id": scenario_id,
                "user_id": user_id,
                "comments": comments,
                "decision_data": decision
            }
        )
        
        if decision['compliant']:
            print("🏆 Issuing Verifiable Credential...")
            report_agent = ReportAgentComponent()
            vc = report_agent.build(
                scenario_id=scenario_id,
                decision=decision,
                evidence_id=wf_id
            )
            print(f"   -> VC ID: {vc['id']}")
        
        print("\n✅ Workflow Status: APPROVED")
        
    else:
        user_id = input("👉 Your ID/Email: ").strip() or "cli-user@hazardsafe.ai"
        comments = input("👉 Reason for rejection: ").strip() or "Rejected by reviewer"
        
        print(f"\n👤 Rejecting as {user_id}...")
        wf_manager.reject_workflow(wf_id, user_id, comments)
        
        # Log rejection to provenance
        prov_agent.build(
            agent_id="CLI",
            event_type="HITL_REJECTED",
            payload={
                "workflow_id": wf_id,
                "scenario_id": scenario_id,
                "user_id": user_id,
                "comments": comments,
                "decision_data": decision
            }
        )
        
        print("\n⛔ Workflow Status: REJECTED")
        print("🚫 No VC issued.")

    print("\n✨ Demo Complete!")
    print(f"\n💡 Tip: Check provenance logs to see full audit trail")

if __name__ == "__main__":
    interactive_hitl_demo()
