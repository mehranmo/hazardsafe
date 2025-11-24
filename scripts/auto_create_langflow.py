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
    "description": "Human-in-the-Loop workflow for HazMat compliance with Verifiable Credentials",
    "data": {
        "nodes": [
            {
                "id": "chat_input_scenario",
                "data": {
                    "type": "ChatInput",
                    "node": {
                        "template": {
                            "input_value": {
                                "type": "str",
                                "value": '{"id": "SCN-DEMO-001", "material_class": "Class 7", "package_type": "Type B(U)", "ambient_temperature_c": 25.0, "transport_index": 0.5}'
                            }
                        },
                        "description": "HazMat Scenario Input"
                    }
                },
                "position": {"x": 100, "y": 200}
            },
            {
                "id": "compliance_agent",
                "data": {
                    "type": "ComplianceAgent",
                    "node": {
                        "description": "Checks compliance using RAG + Code-as-Policy"
                    }
                },
                "position": {"x": 400, "y": 200}
            },
            {
                "id": "chat_input_hitl",
                "data": {
                    "type": "ChatInput",
                    "node": {
                        "template": {
                            "input_value": {
                                "type": "str",
                                "value": "Type 'yes' to approve or 'no' to reject"
                            }
                        },
                        "description": "🛑 HITL: Human Decision Point"
                    }
                },
                "position": {"x": 700, "y": 200}
            },
            {
                "id": "provenance_agent",
                "data": {
                    "type": "ProvenanceAgent",
                    "node": {
                        "description": "Logs decision to immutable ledger"
                    }
                },
                "position": {"x": 1000, "y": 200}
            },
            {
                "id": "report_agent",
                "data": {
                    "type": "ReportAgent",
                    "node": {
                        "description": "Issues Verifiable Credential if approved"
                    }
                },
                "position": {"x": 1300, "y": 200}
            },
            {
                "id": "chat_output",
                "data": {
                    "type": "ChatOutput",
                    "node": {
                        "description": "Final Result"
                    }
                },
                "position": {"x": 1600, "y": 200}
            }
        ],
        "edges": [
            {
                "id": "e1",
                "source": "chat_input_scenario",
                "target": "compliance_agent",
                "sourceHandle": "output",
                "targetHandle": "scenario"
            },
            {
                "id": "e2",
                "source": "compliance_agent",
                "target": "chat_input_hitl",
                "sourceHandle": "decision",
                "targetHandle": "input"
            },
            {
                "id": "e3",
                "source": "chat_input_hitl",
                "target": "provenance_agent",
                "sourceHandle": "output",
                "targetHandle": "decision"
            },
            {
                "id": "e4",
                "source": "compliance_agent",
                "target": "provenance_agent",
                "sourceHandle": "decision",
                "targetHandle": "decision"
            },
            {
                "id": "e5",
                "source": "provenance_agent",
                "target": "report_agent",
                "sourceHandle": "event_log",
                "targetHandle": "evidence_log"
            },
            {
                "id": "e6",
                "source": "compliance_agent",
                "target": "report_agent",
                "sourceHandle": "decision",
                "targetHandle": "decision"
            },
            {
                "id": "e7",
                "source": "report_agent",
                "target": "chat_output",
                "sourceHandle": "vc",
                "targetHandle": "input"
            }
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
