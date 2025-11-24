from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message
import json
import os
import sys

# Add project root to path
sys.path.insert(0, '/home/mmonavar/Projects/aqi/aqi')
from src.agents.compliance_agent import HazardComplianceAgent

class ComplianceAgentComponent(Component):
    display_name = "Compliance Agent"
    description = "Checks HazMat scenarios against regulations using RAG + Code-as-Policy"
    icon = "shield-check"
    name = "ComplianceAgent"

    inputs = [
        MessageTextInput(
            name="scenario",
            display_name="Scenario JSON",
            info="HazMat transport scenario as JSON string",
            value='{"id": "SCN-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}'
        )
    ]

    outputs = [
        Output(
            display_name="Decision",
            name="decision",
            method="check_compliance"
        )
    ]

    def check_compliance(self) -> Message:
        # Parse scenario
        scenario_str = self.scenario
        if isinstance(scenario_str, Message):
            scenario_str = scenario_str.text
        
        try:
            scenario = json.loads(scenario_str)
        except:
            scenario = scenario_str if isinstance(scenario_str, dict) else {}
        
        # Run compliance check
        agent = HazardComplianceAgent()
        decision = agent.check_scenario(scenario)
        
        # Format output
        result_text = f"""
🔍 Compliance Check Result:
- Scenario: {scenario.get('id', 'Unknown')}
- Decision: {'✅ APPROVED' if decision['compliant'] else '❌ REJECTED'}
- Reason: {decision['reason']}
"""
        
        self.status = result_text
        return Message(text=json.dumps(decision))
