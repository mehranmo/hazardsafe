import time
import yaml
import os
from src.utils.firestore_client import FirestoreClient

# Load configuration
CONFIG_PATH = "config/hitl_config.yaml"
DEFAULT_CONFIG = {
    "timeout_hours": 24,
    "auto_reject_on_timeout": True
}

class WorkflowManager:
    # Valid state transitions
    VALID_TRANSITIONS = {
        "DRAFT": ["PENDING_HITL", "CANCELLED"],
        "PENDING_HITL": ["APPROVED", "REJECTED", "TIMEOUT"],
        "APPROVED": [],  # Terminal state
        "REJECTED": [],  # Terminal state
        "TIMEOUT": [],   # Terminal state
        "CANCELLED": []  # Terminal state
    }
    
    def __init__(self):
        self.db = FirestoreClient(collection_name="workflow_state")
        self.config = self._load_config()

    def _load_config(self):
        """Load HITL configuration from YAML file"""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        return DEFAULT_CONFIG

    def create_workflow(self, scenario_id, scenario_data=None):
        """
        Initializes a new workflow state for a scenario.
        """
        state = {
            "scenario_id": scenario_id,
            "scenario_data": scenario_data or {},
            "status": "DRAFT",
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
            "history": [],
            "current_step": "init",
            "decision_data": None,
            "human_reviewer": None,
            "human_comments": None
        }
        doc_id = self.db.add_document(state)
        print(f"[Workflow] Created new workflow for {scenario_id} (ID: {doc_id})")
        return doc_id

    def _validate_transition(self, current_status, new_status):
        """Validate if a state transition is allowed"""
        if current_status not in self.VALID_TRANSITIONS:
            raise ValueError(f"Invalid current status: {current_status}")
        
        allowed = self.VALID_TRANSITIONS[current_status]
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {current_status} -> {new_status}. "
                f"Allowed: {allowed}"
            )

    def _update_status(self, doc_id, new_status, metadata=None):
        """Internal method to update workflow status with validation"""
        # Get current state
        current_state = self.db.get_document(doc_id)
        if not current_state:
            raise ValueError(f"Workflow {doc_id} not found")
        
        current_status = current_state.get("status")
        
        # Validate transition
        self._validate_transition(current_status, new_status)
        
        # Update document
        update_data = {
            "status": new_status,
            "updated_at": int(time.time())
        }
        
        if metadata:
            update_data.update(metadata)
        
        # Add to history
        history_entry = {
            "from_status": current_status,
            "to_status": new_status,
            "timestamp": int(time.time()),
            "metadata": metadata or {}
        }
        
        # Get current history and append
        current_history = current_state.get("history", [])
        current_history.append(history_entry)
        update_data["history"] = current_history
        
        self.db.update_document(doc_id, update_data)
        print(f"[Workflow] Updated {doc_id}: {current_status} -> {new_status}")
        
        return update_data

    def trigger_hitl(self, workflow_id, decision_data):
        """
        Transition workflow to PENDING_HITL state.
        This is called when human review is required.
        
        Args:
            workflow_id: The workflow document ID
            decision_data: The AI's decision/recommendation that needs review
        """
        metadata = {
            "decision_data": decision_data,
            "hitl_triggered_at": int(time.time())
        }
        
        self._update_status(workflow_id, "PENDING_HITL", metadata)
        print(f"[Workflow] HITL triggered for {workflow_id}")
        print(f"[Workflow] Awaiting human review...")
        
        return {
            "workflow_id": workflow_id,
            "status": "PENDING_HITL",
            "message": "Workflow is now pending human review"
        }

    def approve_workflow(self, workflow_id, user_id, comments=""):
        """
        Human approves the workflow.
        
        Args:
            workflow_id: The workflow document ID
            user_id: ID/email of the approving user
            comments: Optional comments from the reviewer
        """
        metadata = {
            "human_reviewer": user_id,
            "human_comments": comments,
            "human_decision": "APPROVED",
            "decision_timestamp": int(time.time())
        }
        
        self._update_status(workflow_id, "APPROVED", metadata)
        print(f"[Workflow] Approved by {user_id}")
        
        return {
            "workflow_id": workflow_id,
            "status": "APPROVED",
            "reviewer": user_id,
            "comments": comments
        }

    def reject_workflow(self, workflow_id, user_id, comments=""):
        """
        Human rejects the workflow.
        
        Args:
            workflow_id: The workflow document ID
            user_id: ID/email of the rejecting user
            comments: Reason for rejection
        """
        metadata = {
            "human_reviewer": user_id,
            "human_comments": comments,
            "human_decision": "REJECTED",
            "decision_timestamp": int(time.time())
        }
        
        self._update_status(workflow_id, "REJECTED", metadata)
        print(f"[Workflow] Rejected by {user_id}: {comments}")
        
        return {
            "workflow_id": workflow_id,
            "status": "REJECTED",
            "reviewer": user_id,
            "comments": comments
        }

    def check_timeouts(self):
        """
        Check for workflows that have exceeded timeout and auto-reject them.
        Returns list of timed-out workflow IDs.
        """
        if not self.config.get("auto_reject_on_timeout", True):
            return []
        
        timeout_hours = self.config.get("timeout_hours", 24)
        timeout_seconds = timeout_hours * 3600
        current_time = int(time.time())
        
        # Query for PENDING_HITL workflows
        pending_workflows = self.db.query_documents({"status": "PENDING_HITL"})
        
        timed_out = []
        for workflow in pending_workflows:
            hitl_triggered_at = workflow.get("hitl_triggered_at", workflow.get("created_at", 0))
            age = current_time - hitl_triggered_at
            
            if age > timeout_seconds:
                workflow_id = workflow.get("id")
                print(f"[Workflow] Timeout detected for {workflow_id} (age: {age/3600:.1f} hours)")
                
                try:
                    metadata = {
                        "timeout_reason": f"No human decision within {timeout_hours} hours",
                        "auto_rejected": True
                    }
                    self._update_status(workflow_id, "TIMEOUT", metadata)
                    timed_out.append(workflow_id)
                except Exception as e:
                    print(f"[Workflow] Error timing out {workflow_id}: {e}")
        
        return timed_out

    def get_workflow_state(self, doc_id):
        """Get the current state of a workflow"""
        return self.db.get_document(doc_id)

    def get_pending_workflows(self):
        """Get all workflows pending human review"""
        return self.db.query_documents({"status": "PENDING_HITL"})

    def update_status(self, doc_id, new_status, metadata=None):
        """
        Legacy method for backward compatibility.
        Use specific methods (trigger_hitl, approve_workflow, etc.) instead.
        """
        return self._update_status(doc_id, new_status, metadata)
