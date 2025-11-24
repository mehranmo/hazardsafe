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
    
    # 3. HITL Approval
    print("\n[Node 3] HITL Approval")
    print(f"Compliance Result: {decision}")
    approval = input(">>> Approve this scenario? (yes/no): ").strip().lower()
    
    # 4. Conditional Logic
    if approval == 'yes':
        print("\n[Node 4] Conditional: APPROVED")
        
        # 5. Provenance Agent: Log Approval
        print("\n[Node 5] Provenance Agent: Log Approval")
        prov_agent = ProvenanceAgentComponent()
        log_result = prov_agent.build(agent_id="HITL_Reviewer", event_type="APPROVAL", payload={"decision": "APPROVED"})
        evidence_id = log_result['doc_id']
        print(f"Log ID: {evidence_id}")
        
        # 6. Report Agent: Issue VC
        print("\n[Node 6] Report Agent: Issue VC")
        report_agent = ReportAgentComponent()
        vc = report_agent.build(scenario_id="SCN-LANGFLOW-001", decision=decision, evidence_id=evidence_id)
        print(f"VC Issued: {vc['id']}")
        print(f"VC Content: {vc}")
        
        # 7. Workflow Manager: Update Status
        print("\n[Node 7] Workflow Manager: Update to APPROVED")
        wf_comp.build(action="Update", doc_id=wf_id, status="APPROVED")
        
    else:
        print("\n[Node 4] Conditional: REJECTED")
        
        # 5. Provenance Agent: Log Rejection
        print("\n[Node 5] Provenance Agent: Log Rejection")
        prov_agent = ProvenanceAgentComponent()
        log_result = prov_agent.build(agent_id="HITL_Reviewer", event_type="REJECTION", payload={"decision": "REJECTED"})
        evidence_id = log_result['doc_id']
        print(f"Log ID: {evidence_id}")
        
        # 6. Report Agent: Issue Rejection Report
        print("\n[Node 6] Report Agent: Issue Rejection Report")
        report_agent = ReportAgentComponent()
        # Assuming ReportAgent can handle rejection or we just log it
        print("Rejection recorded.")
        
        # 7. Workflow Manager: Update Status
        print("\n[Node 7] Workflow Manager: Update to REJECTED")
        wf_comp.build(action="Update", doc_id=wf_id, status="REJECTED")

    print("\n--- Simulation Complete ---")

if __name__ == "__main__":
    simulate_langflow_execution()
