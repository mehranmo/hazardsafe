#!/usr/bin/env python3
"""
Automatically creates the HazardSAFE HITL workflow in LangFlow using the API.
"""

import requests
import json
import time

LANGFLOW_URL = "http://localhost:7860"
FLOW_NAME = "HazardSAFE HITL Workflow"

# Define the flow structure
flow_data = {
    "name": FLOW_NAME,
    "description": "Human-in-the-Loop workflow: scenario -> compliance -> human approval -> provenance -> VC issuance -> output (approval) or rejection output.",
    "folder_name": "HazardSAFE",
    "data": {
        "nodes": [
            {
                "id": "node_1",
                "type": "ChatInput",
                "data": {
                    "label": "Scenario Input",
                    "description": "Paste the JSON scenario here",
                    "field_name": "scenario",
                    "value": '{"id": "SCN-DEMO-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}'
                },
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "node_2",
                "type": "ComplianceAgent",
                "data": {
                    "label": "Compliance Agent",
                    "description": "Runs the HazardComplianceAgent on the scenario"
                },
                "position": {"x": 250, "y": 0}
            },
            {
                "id": "node_3",
                "type": "ChatInput",
                "data": {
                    "label": "HITL Approval",
                    "description": "Human approves (yes/no) the compliance result",
                    "field_name": "approval",
                    "value": ""
                },
                "position": {"x": 500, "y": -100}
            },
            {
                "id": "node_4",
                "type": "Conditional",
                "data": {
                    "label": "Approval Check",
                    "condition": "{{approval}} == 'yes'",
                    "true_node": "node_5",
                    "false_node": "node_9"
                },
                "position": {"x": 750, "y": -50}
            },
            {
                "id": "node_5",
                "type": "ProvenanceAgent",
                "data": {
                    "label": "Provenance (Approved)",
                    "description": "Logs the approved decision"
                },
                "position": {"x": 1000, "y": -100}
            },
            {
                "id": "node_6",
                "type": "ReportAgent",
                "data": {
                    "label": "Report & VC Agent (Approved)",
                    "description": "Issues a Verifiable Credential for the approved scenario"
                },
                "position": {"x": 1250, "y": -100}
            },
            {
                "id": "node_8",
                "type": "ChatOutput",
                "data": {
                    "label": "Final Output",
                    "description": "Shows the VC or success message"
                },
                "position": {"x": 1500, "y": -100}
            },
            {
                "id": "node_9",
                "type": "ProvenanceAgent",
                "data": {
                    "label": "Provenance (Rejected)",
                    "description": "Logs the rejected decision"
                },
                "position": {"x": 1000, "y": 100}
            },
            {
                "id": "node_10",
                "type": "ReportAgent",
                "data": {
                    "label": "Report & VC Agent (Rejected)",
                    "description": "Issues a rejection report / VC for the denied scenario"
                },
                "position": {"x": 1250, "y": 100}
            },
            {
                "id": "node_7",
                "type": "ChatOutput",
                "data": {
                    "label": "Rejection Output",
                    "description": "Shows why the scenario was rejected"
                },
                "position": {"x": 1500, "y": 100}
            }
        ],
        "edges": [
            {"source": "node_1", "target": "node_2"},
            {"source": "node_2", "target": "node_3"},
            {"source": "node_3", "target": "node_4"},
            {"source": "node_4", "target": "node_5", "condition": "true"},
            {"source": "node_4", "target": "node_9", "condition": "false"},
            {"source": "node_5", "target": "node_6"},
            {"source": "node_6", "target": "node_8"},
            {"source": "node_9", "target": "node_10"},
            {"source": "node_10", "target": "node_7"}
        ]
    }
}

def create_flow():
    """Create the flow using LangFlow API"""
    print(f"🔄 Attempting to create flow '{FLOW_NAME}' in LangFlow...")
    
    # Check if LangFlow is running
    try:
        health_url = f"{LANGFLOW_URL}/health"
        response = requests.get(health_url, timeout=5)
        print(f"✅ LangFlow is running at {LANGFLOW_URL}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: LangFlow is not running at {LANGFLOW_URL}")
        print(f"   Start it with: python3 -m langflow run")
        return False
    
    # Try to create via API
    try:
        create_url = f"{LANGFLOW_URL}/api/v1/flows/"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            create_url,
            json=flow_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            flow_id = result.get('id', 'unknown')
            print(f"✅ Flow created successfully!")
            print(f"   Flow ID: {flow_id}")
            print(f"   Access it at: {LANGFLOW_URL}")
            return True
        elif response.status_code == 403:
            print(f"⚠️  Authentication required (LangFlow v1.5+)")
            print(f"\n🔧 WORKAROUND: Restart LangFlow without auth:")
            print(f"   1. Stop current LangFlow (Ctrl+C)")
            print(f"   2. Run:")
            print(f"      LANGFLOW_SKIP_AUTH_AUTO_LOGIN=true python3 -m langflow run")
            print(f"   3. Or use the manual method below")
            return False
        else:
            print(f"⚠️  API error (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not create flow via API: {e}")
        return False

def print_manual_instructions():
    """Print manual setup instructions"""
    print(f"\n{'='*70}")
    print("  ✋ MANUAL SETUP (Recommended)")
    print(f"{'='*70}\n")
    print("The HazardSAFE components are already loaded in LangFlow!")
    print("\n📋 Steps:")
    print(f"  1. Open: {LANGFLOW_URL}")
    print("  2. Click '+ New Flow'")
    print("  3. Find 'HazardSAFE' in the left sidebar")
    print("  4. Drag these components onto the canvas:")
    print("     • Compliance Agent")
    print("     • Provenance Agent")
    print("     • Report Agent")
    print("  5. Add Chat Input/Output nodes")
    print("  6. Connect them in order")
    print("\n💡 Pre-loaded scenario:")
    print('     {"id": "SCN-DEMO-001", "material_class": "Class 7",')
    print('      "package_type": "Type B(U)", "ambient_temperature_c": 25.0}')
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  HazardSAFE Auto-Flow Creator for LangFlow")
    print("="*70 + "\n")
    
    success = create_flow()
    
    if not success:
        print_manual_instructions()
    
    print(f"🌐 LangFlow UI: {LANGFLOW_URL}\n")
