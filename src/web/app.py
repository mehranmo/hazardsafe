#!/usr/bin/env python3
"""
HazardSAFE HITL Web UI

Flask-based web interface for human reviewers to approve/reject workflows.

Usage:
    python3 src/web/app.py
    
Or use the startup script:
    ./scripts/start_web_ui.sh
"""

from flask import Flask, render_template, request, jsonify
import yaml
import os
import sys
import random
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflow.manager import WorkflowManager
from src.agents.provenance_agent import HazardProvenanceAgent
from src.agents.compliance_agent import HazardComplianceAgent

app = Flask(__name__)

# Load configuration
CONFIG_PATH = "config/hitl_config.yaml"
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

# Initialize managers
workflow_manager = WorkflowManager()
provenance_agent = HazardProvenanceAgent()

# Simple API key authentication
API_KEY = config.get('web_ui', {}).get('api_key', 'hazardsafe-demo-key')

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def dashboard():
    """Main dashboard showing pending approvals"""
    return render_template('dashboard.html', api_key=API_KEY)

@app.route('/api/pending')
def get_pending():
    """Get all workflows pending human review"""
    try:
        pending = workflow_manager.get_pending_workflows()
        
        # Enrich with additional info
        enriched = []
        for workflow in pending:
            enriched.append({
                "id": workflow.get("id"),
                "scenario_id": workflow.get("scenario_id"),
                "scenario_data": workflow.get("scenario_data", {}),
                "decision_data": workflow.get("decision_data", {}),
                "created_at": workflow.get("created_at"),
                "hitl_triggered_at": workflow.get("hitl_triggered_at"),
                "age_hours": (workflow.get("updated_at", 0) - workflow.get("hitl_triggered_at", 0)) / 3600
            })
        
        return jsonify({
            "success": True,
            "count": len(enriched),
            "workflows": enriched
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflow/<workflow_id>')
def get_workflow(workflow_id):
    """Get details of a specific workflow"""
    try:
        workflow = workflow_manager.get_workflow_state(workflow_id)
        if not workflow:
            return jsonify({"success": False, "error": "Workflow not found"}), 404
        
        return jsonify({
            "success": True,
            "workflow": workflow
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/approve/<workflow_id>', methods=['POST'])
@require_api_key
def approve_workflow(workflow_id):
    """Approve a workflow"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        comments = data.get('comments', '')
        
        # Approve the workflow
        result = workflow_manager.approve_workflow(workflow_id, user_id, comments)
        
        # Log to provenance
        workflow_state = workflow_manager.get_workflow_state(workflow_id)
        provenance_agent.log_event(
            event_type="HITL_APPROVED",
            agent_id="WebUI",
            payload={
                "workflow_id": workflow_id,
                "scenario_id": workflow_state.get("scenario_id"),
                "user_id": user_id,
                "comments": comments,
                "decision_data": workflow_state.get("decision_data")
            }
        )
        
        return jsonify({
            "success": True,
            "result": result,
            "message": f"Workflow approved by {user_id}"
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reject/<workflow_id>', methods=['POST'])
@require_api_key
def reject_workflow(workflow_id):
    """Reject a workflow"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        comments = data.get('comments', 'No reason provided')
        
        # Reject the workflow
        result = workflow_manager.reject_workflow(workflow_id, user_id, comments)
        
        # Log to provenance
        workflow_state = workflow_manager.get_workflow_state(workflow_id)
        provenance_agent.log_event(
            event_type="HITL_REJECTED",
            agent_id="WebUI",
            payload={
                "workflow_id": workflow_id,
                "scenario_id": workflow_state.get("scenario_id"),
                "user_id": user_id,
                "comments": comments,
                "decision_data": workflow_state.get("decision_data")
            }
        )
        
        return jsonify({
            "success": True,
            "result": result,
            "message": f"Workflow rejected by {user_id}"
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        pending = workflow_manager.get_pending_workflows()
        
        return jsonify({
            "success": True,
            "stats": {
                "pending_count": len(pending),
                "timeout_hours": config.get('timeout_hours', 24)
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-test', methods=['POST'])
@require_api_key
def generate_test():
    """Generate a mock test scenario"""
    try:
        data = request.get_json() or {}
        scenario_type = data.get('type', 'random')
        
        # Generate scenario based on type
        scenarios = {
            'pass': {
                'material_class': 'Class 7',
                'package_type': 'Type B(U)',
                'ambient_temperature_c': round(random.uniform(20, 35), 1),
                'transport_index': round(random.uniform(0.1, 0.9), 2)
            },
            'fail': {
                'material_class': 'Class 7',
                'package_type': 'Type B(U)',
                'ambient_temperature_c': round(random.uniform(40, 50), 1),
                'transport_index': round(random.uniform(0.1, 0.9), 2)
            },
            'edge': {
                'material_class': 'Class 7',
                'package_type': 'Type B(U)',
                'ambient_temperature_c': 38.0,  # Exactly at limit
                'transport_index': round(random.uniform(0.1, 0.9), 2)
            }
        }
        
        if scenario_type == 'random':
            scenario_type = random.choice(['pass', 'fail', 'edge'])
        
        scenario = scenarios.get(scenario_type, scenarios['pass'])
        scenario_id = f"TEST-{scenario_type.upper()}-{int(time.time())}"
        scenario['id'] = scenario_id
        
        # Create workflow
        wf_id = workflow_manager.create_workflow(scenario_id, scenario)
        
        # Get AI decision
        compliance_agent = HazardComplianceAgent()
        decision = compliance_agent.check_scenario(scenario)
        
        # Trigger HITL
        workflow_manager.trigger_hitl(wf_id, decision)
        
        # Log to provenance
        provenance_agent.log_event(
            event_type="HITL_TRIGGERED",
            agent_id="WebUI-TestGenerator",
            payload={
                "workflow_id": wf_id,
                "scenario_id": scenario_id,
                "test_type": scenario_type,
                "decision_data": decision
            }
        )
        
        return jsonify({
            "success": True,
            "workflow_id": wf_id,
            "scenario": scenario,
            "decision": decision,
            "message": f"Generated {scenario_type} test scenario"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get workflow history for audit"""
    try:
        # Get all workflows from Firestore
        all_workflows = workflow_manager.db.get_all_documents()
        
        # Sort by timestamp (newest first)
        all_workflows.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        # Limit to last 50
        history = all_workflows[:50]
        
        # Enrich with additional info
        enriched = []
        for wf in history:
            enriched.append({
                "id": wf.get("id"),
                "scenario_id": wf.get("scenario_id"),
                "status": wf.get("status"),
                "created_at": wf.get("created_at"),
                "updated_at": wf.get("updated_at"),
                "human_reviewer": wf.get("human_reviewer"),
                "human_comments": wf.get("human_comments"),
                "decision_data": wf.get("decision_data", {}),
                "history": wf.get("history", [])
            })
        
        return jsonify({
            "success": True,
            "count": len(enriched),
            "workflows": enriched
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/architecture')
def get_architecture():
    """Get workflow architecture information"""
    return jsonify({
        "success": True,
        "architecture": {
            "states": [
                {"name": "DRAFT", "description": "Initial workflow creation", "terminal": False},
                {"name": "PENDING_HITL", "description": "Awaiting human review", "terminal": False},
                {"name": "APPROVED", "description": "Human approved", "terminal": True},
                {"name": "REJECTED", "description": "Human rejected", "terminal": True},
                {"name": "TIMEOUT", "description": "Auto-rejected due to timeout", "terminal": True},
                {"name": "CANCELLED", "description": "Workflow cancelled", "terminal": True}
            ],
            "transitions": [
                {"from": "DRAFT", "to": "PENDING_HITL", "trigger": "AI decision requires review"},
                {"from": "DRAFT", "to": "CANCELLED", "trigger": "Manual cancellation"},
                {"from": "PENDING_HITL", "to": "APPROVED", "trigger": "Human approval"},
                {"from": "PENDING_HITL", "to": "REJECTED", "trigger": "Human rejection"},
                {"from": "PENDING_HITL", "to": "TIMEOUT", "trigger": "Timeout exceeded"}
            ],
            "agents": [
                {"name": "Compliance Agent", "role": "Analyzes scenarios against regulations"},
                {"name": "Provenance Agent", "role": "Logs all events to immutable ledger"},
                {"name": "Report Agent", "role": "Issues Verifiable Credentials"},
                {"name": "Workflow Manager", "role": "Manages state transitions"}
            ]
        }
    })

if __name__ == '__main__':
    host = config.get('web_ui', {}).get('host', '0.0.0.0')
    port = config.get('web_ui', {}).get('port', 5000)
    debug = config.get('web_ui', {}).get('debug', True)
    
    print(f"\n{'='*60}")
    print(f"  HazardSAFE HITL Web UI")
    print(f"{'='*60}")
    print(f"  URL: http://{host}:{port}")
    print(f"  API Key: {API_KEY}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)
