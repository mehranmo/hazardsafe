import time
from src.utils.firestore_client import FirestoreClient

class WorkflowManager:
    def __init__(self):
        self.db = FirestoreClient(collection_name="workflow_state")

    def create_workflow(self, scenario_id):
        """
        Initializes a new workflow state for a scenario.
        """
        state = {
            "scenario_id": scenario_id,
            "status": "DRAFT",
            "created_at": int(time.time()),
            "history": [],
            "current_step": "init"
        }
        doc_id = self.db.add_document(state)
        print(f"[Workflow] Created new workflow for {scenario_id} (ID: {doc_id})")
        return doc_id

    def update_status(self, doc_id, new_status, metadata=None):
        """
        Updates the status of a workflow.
        """
        # In a real app, we would fetch, update, and save.
        # Our simple FirestoreClient only supports 'add' (append-only log style) or we need to implement update.
        # For this prototype, we'll just log a new state entry effectively "updating" the view of the state.
        # Or better, let's just assume we are appending state changes to the 'workflow_events' collection 
        # and the "current state" is the latest event.
        
        # But to keep it simple and consistent with the 'add_document' limitation of our mock client:
        # We will log a "State Change" event.
        
        event = {
            "workflow_doc_id": doc_id,
            "status": new_status,
            "timestamp": int(time.time()),
            "metadata": metadata or {}
        }
        self.db.add_document(event)
        print(f"[Workflow] Updated {doc_id} to {new_status}")
        return event

    def get_workflow_state(self, doc_id):
        # This would require querying by ID, which our mock client doesn't efficiently support 
        # (it returns all).
        # For the prototype, we'll just return the last known state if we were tracking it in memory,
        # or scan the mock DB.
        all_docs = self.db.get_all_documents()
        # Filter for this doc_id
        relevant = [d for d in all_docs if d.get('workflow_doc_id') == doc_id or d.get('id') == doc_id]
        # Sort by timestamp
        relevant.sort(key=lambda x: x.get('timestamp', 0))
        
        if not relevant:
            return None
            
        # Reconstruct state
        current_status = "UNKNOWN"
        for event in relevant:
            if 'status' in event:
                current_status = event['status']
                
        return {"doc_id": doc_id, "status": current_status, "history": relevant}
