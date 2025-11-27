#!/usr/bin/env python3
"""
Quick test to create a pending workflow for web UI demonstration
"""

import sys
import time
from src.workflow.manager import WorkflowManager
from src.agents.compliance_agent import HazardComplianceAgent
from src.agents.provenance_agent import HazardProvenanceAgent

def create_test_workflow():
    print("\n" + "="*60)
    print("  Creating Test Workflow for Web UI Demo")
    print("="*60 + "\n")
    
    # Initialize
    wf_manager = WorkflowManager()
    compliance_agent = HazardComplianceAgent()
    prov_agent = HazardProvenanceAgent()
    
    # Create scenario
    scenario = {
        "id": "SCN-WEBUI-TEST-001",
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 30.0,
        "transport_index": 0.8
    }
    
    print(f"📄 Scenario: {scenario['id']}")
    print(f"   Temperature: {scenario['ambient_temperature_c']}°C")
    print(f"   Material: {scenario['material_class']}\n")
    
    # Create workflow
    wf_id = wf_manager.create_workflow(scenario["id"], scenario)
    
    # Get AI decision
    print("🤖 Getting AI recommendation...")
    decision = compliance_agent.check_scenario(scenario)
    print(f"   Decision: {'✅ Compliant' if decision['compliant'] else '❌ Non-Compliant'}")
    print(f"   Reason: {decision['reason']}\n")
    
    # Trigger HITL
    print("🛑 Triggering HITL...")
    wf_manager.trigger_hitl(wf_id, decision)
    
    # Log to provenance
    prov_agent.log_event(
        event_type="HITL_TRIGGERED",
        agent_id="TestScript",
        payload={
            "workflow_id": wf_id,
            "scenario_id": scenario["id"],
            "decision_data": decision
        }
    )
    
    print("\n" + "="*60)
    print("  ✅ Test Workflow Created!")
    print("="*60)
    print(f"\n  Workflow ID: {wf_id}")
    print(f"  Status: PENDING_HITL")
    print(f"\n  Next Steps:")
    print(f"  1. Start web UI: ./scripts/start_web_ui.sh")
    print(f"  2. Open: http://localhost:5000")
    print(f"  3. Review and approve/reject the workflow")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    create_test_workflow()
