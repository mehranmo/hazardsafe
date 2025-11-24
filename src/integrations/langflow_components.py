from typing import Optional, Dict, Any
# We assume langflow is installed or these are just definitions to be pasted into LangFlow
# If langflow is not installed, we define a dummy CustomComponent for the code to be valid python.

try:
    from langflow.custom import CustomComponent
except ImportError:
    # Dummy class for dev environment if langflow not present
    class CustomComponent:
        def build_config(self): return {}
        def build(self, **kwargs): pass

from src.agents.compliance_agent import HazardComplianceAgent
from src.agents.provenance_agent import HazardProvenanceAgent
from src.agents.report_agent import ReportAgent
from src.workflow.manager import WorkflowManager

class ComplianceAgentComponent(CustomComponent):
    display_name = "Hazard Compliance Agent"
    description = "Checks a HazMat scenario against regulations."

    def build_config(self):
        return {
            "scenario": {"display_name": "Scenario JSON", "field_type": "dict"},
            "model_name": {"display_name": "Model Name", "value": "gemini-2.0-flash-exp"}
        }

    def build(self, scenario: dict, model_name: str = "gemini-2.0-flash-exp") -> dict:
        agent = HazardComplianceAgent(model_name=model_name)
        result = agent.check_scenario(scenario)
        return result

class ProvenanceAgentComponent(CustomComponent):
    display_name = "Hazard Provenance Agent"
    description = "Logs events to the immutable ledger."

    def build_config(self):
        return {
            "agent_id": {"display_name": "Source Agent ID", "field_type": "str"},
            "event_type": {"display_name": "Event Type", "field_type": "str"},
            "payload": {"display_name": "Event Payload", "field_type": "dict"}
        }

    def build(self, agent_id: str, event_type: str, payload: dict) -> dict:
        agent = HazardProvenanceAgent()
        # In a real flow, we would pass the signature from the previous node.
        # For simplicity in this component, we just log.
        result = agent.log_event(event_type, agent_id, payload)
        return result

class ReportAgentComponent(CustomComponent):
    display_name = "Report & VC Agent"
    description = "Issues a Verifiable Credential if compliant."

    def build_config(self):
        return {
            "scenario_id": {"display_name": "Scenario ID", "field_type": "str"},
            "decision": {"display_name": "Compliance Decision", "field_type": "dict"},
            "evidence_id": {"display_name": "Evidence ID", "field_type": "str"}
        }

    def build(self, scenario_id: str, decision: dict, evidence_id: str) -> dict:
        agent = ReportAgent()
        vc = agent.issue_vc(scenario_id, decision, evidence_id)
        return vc

class WorkflowManagerComponent(CustomComponent):
    display_name = "Workflow Manager"
    description = "Manages the state of the assessment workflow."

    def build_config(self):
        return {
            "action": {"display_name": "Action", "options": ["Create", "Update"], "value": "Update"},
            "doc_id": {"display_name": "Document ID (for Update)", "field_type": "str"},
            "status": {"display_name": "New Status", "field_type": "str"},
            "scenario_id": {"display_name": "Scenario ID (for Create)", "field_type": "str"}
        }

    def build(self, action: str, doc_id: Optional[str] = None, status: Optional[str] = None, scenario_id: Optional[str] = None) -> str:
        mgr = WorkflowManager()
        if action == "Create":
            return mgr.create_workflow(scenario_id)
        elif action == "Update":
            mgr.update_status(doc_id, status)
            return doc_id
        return "Invalid Action"
