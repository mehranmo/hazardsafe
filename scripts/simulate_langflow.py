from src.integrations.langflow_components import ComplianceAgentComponent, ProvenanceAgentComponent, ReportAgentComponent, WorkflowManagerComponent

def simulate_langflow_execution():
    print("--- Simulating LangFlow Execution ---")
    
    # 1. Workflow Manager: Create Workflow
    print("\n[Node 1] Workflow Manager: Create")
    wf_comp = WorkflowManagerComponent()
    wf_id = wf_comp.build(action="Create", scenario_id="SCN-LANGFLOW-001")
    print(f"Workflow ID: {wf_id}")
    
    # 2. Compliance Agent: Check Scenario
    print("\n[Node 2] Compliance Agent: Check")
    scenario = {
        "id": "SCN-LANGFLOW-001",
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 25, # Compliant
        "transport_index": 0.5
    }
    comp_agent = ComplianceAgentComponent()
    decision = comp_agent.build(scenario=scenario)
    print(f"Decision: {decision['compliant']}")
    
    # 3. Provenance Agent: Log Decision
    print("\n[Node 3] Provenance Agent: Log")
    prov_agent = ProvenanceAgentComponent()
    log_result = prov_agent.build(agent_id="ComplianceAgent", event_type="DECISION_MADE", payload=decision)
    evidence_id = log_result['doc_id']
    print(f"Log ID: {evidence_id}")
    
    # 4. Report Agent: Issue VC (if compliant)
    if decision['compliant']:
        print("\n[Node 4] Report Agent: Issue VC")
        report_agent = ReportAgentComponent()
        vc = report_agent.build(scenario_id="SCN-LANGFLOW-001", decision=decision, evidence_id=evidence_id)
        print(f"VC Issued: {vc['id']}")
        
        # 5. Workflow Manager: Update Status
        print("\n[Node 5] Workflow Manager: Update to APPROVED")
        wf_comp.build(action="Update", doc_id=wf_id, status="APPROVED")
    else:
        print("\n[Node 4] Workflow Manager: Update to REJECTED")
        wf_comp.build(action="Update", doc_id=wf_id, status="REJECTED")

    print("\n--- Simulation Complete ---")

if __name__ == "__main__":
    simulate_langflow_execution()
