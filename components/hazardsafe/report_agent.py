from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message
import json
import sys

sys.path.insert(0, '/home/mmonavar/Projects/aqi/aqi')
from src.agents.report_agent import ReportAgent

class ReportAgentComponent(Component):
    display_name = "Report & VC Agent"
    description = "Issues Verifiable Credentials for approved scenarios"
    icon = "award"
    name = "ReportAgent"

    inputs = [
        MessageTextInput(
            name="decision",
            display_name="Compliance Decision",
            info="Decision JSON from Compliance Agent"
        ),
        MessageTextInput(
            name="evidence_log",
            display_name="Evidence Log",
            info="Log result from Provenance Agent"
        ),
        MessageTextInput(
            name="scenario_id",
            display_name="Scenario ID",
            value="SCN-001"
        )
    ]

    outputs = [
        Output(
            display_name="Verifiable Credential",
            name="vc",
            method="issue_vc"
        )
    ]

    def issue_vc(self) -> Message:
        decision_str = self.decision
        if isinstance(decision_str, Message):
            decision_str = decision_str.text
        
        try:
            decision = json.loads(decision_str)
        except:
            decision = decision_str if isinstance(decision_str, dict) else {}
        
        evidence_str = self.evidence_log
        if isinstance(evidence_str, Message):
            evidence_str = evidence_str.text
        
        try:
            evidence = json.loads(evidence_str)
            evidence_id = evidence.get('doc_id', 'unknown')
        except:
            evidence_id = 'unknown'
        
        if not decision.get('compliant'):
            result_text = "⛔ Scenario not compliant - No VC issued"
            self.status = result_text
            return Message(text=json.dumps({"status": "skipped", "reason": "non-compliant"}))
        
        agent = ReportAgent()
        vc = agent.issue_vc(self.scenario_id, decision, evidence_id)
        
        result_text = f"🏆 VC Issued: {vc['id']}"
        self.status = result_text
        
        return Message(text=json.dumps(vc, indent=2))
