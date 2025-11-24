from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message
import json
import sys

sys.path.insert(0, '/home/mmonavar/Projects/aqi/aqi')
from src.agents.provenance_agent import HazardProvenanceAgent

class ProvenanceAgentComponent(Component):
    display_name = "Provenance Agent"
    description = "Logs compliance decisions to immutable ledger"
    icon = "database"
    name = "ProvenanceAgent"

    inputs = [
        MessageTextInput(
            name="decision",
            display_name="Decision",
            info="Compliance decision JSON"
        ),
        MessageTextInput(
            name="agent_id",
            display_name="Source Agent ID",
            value="ComplianceAgent"
        )
    ]

    outputs = [
        Output(
            display_name="Event Log",
            name="event_log",
            method="log_event"
        )
    ]

    def log_event(self) -> Message:
        decision_str = self.decision
        if isinstance(decision_str, Message):
            decision_str = decision_str.text
        
        try:
            decision = json.loads(decision_str)
        except:
            decision = decision_str if isinstance(decision_str, dict) else {}
        
        agent = HazardProvenanceAgent()
        result = agent.log_event(
            event_type="COMPLIANCE_CHECK",
            agent_id=self.agent_id,
            payload=decision
        )
        
        log_text = f"📝 Logged to ledger: {result['doc_id']}"
        self.status = log_text
        
        return Message(text=json.dumps(result))
