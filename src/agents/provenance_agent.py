import json
from src.utils.firestore_client import FirestoreClient
from src.security.interceptor import MessageSigner
from src.security.agent_card import AgentCardManager

class HazardProvenanceAgent:
    def __init__(self):
        self.agent_name = "HazardProvenanceAgent"
        self.card_manager = AgentCardManager(self.agent_name)
        self.agent_card = self.card_manager.create_agent_card(
            capabilities=["LogEvent", "GetProvenanceGraph"],
            description="Immutable ledger for HazMat lifecycle events."
        )
        
        self.db = FirestoreClient()
        self.signer = MessageSigner(self.agent_name)

    def log_event(self, event_type, agent_id, payload, signature=None):
        """
        Logs an event to Firestore. 
        Verifies signature if provided (simulating A2A security check).
        
        HITL Event Types:
        - HITL_TRIGGERED: When workflow enters PENDING_HITL
        - HITL_APPROVED: Human approval with user_id and comments
        - HITL_REJECTED: Human rejection with user_id and comments  
        - HITL_TIMEOUT: Auto-rejection due to timeout
        """
        print(f"[{self.agent_name}] Logging event: {event_type} from {agent_id}")
        
        # In a real A2A call, 'payload' would be inside the signed message.
        # Here we simulate that check:
        if signature:
            verified_payload = self.signer.verify_message(signature)
            if verified_payload != payload:
                print(f"[{self.agent_name}] ⚠️ SECURITY ALERT: Signature mismatch!")
                # We log the security failure too
                self.db.add_document({
                    "type": "SECURITY_ALERT",
                    "agent_id": agent_id,
                    "details": "Signature verification failed",
                    "raw_signature": signature
                })
                return {"success": False, "error": "Invalid Signature"}
        
        event_doc = {
            "type": event_type,
            "agent_id": agent_id,
            "payload": payload,
            "signature_verified": bool(signature)
        }
        
        # Add HITL-specific metadata if applicable
        if event_type.startswith("HITL_"):
            event_doc["category"] = "human_in_the_loop"
            if "user_id" in payload:
                event_doc["human_actor"] = payload["user_id"]
        
        doc_id = self.db.add_document(event_doc)
        print(f"[{self.agent_name}] Event logged with ID: {doc_id}")
        return {"success": True, "doc_id": doc_id}

    def get_provenance_graph(self):
        return self.db.get_all_documents()

if __name__ == "__main__":
    # Test
    agent = HazardProvenanceAgent()
    
    # Simulate a signed message from Compliance Agent
    signer = MessageSigner("ComplianceAgent")
    msg = {"decision": "Approved", "reason": "Temp OK"}
    sig = signer.sign_message(msg)
    
    agent.log_event("COMPLIANCE_CHECK", "ComplianceAgent", msg, signature=sig)
    
    print("\nProvenance Graph:")
    print(json.dumps(agent.get_provenance_graph(), indent=2))
