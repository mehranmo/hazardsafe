import json
import time
import uuid
from src.security.agent_card import AgentCardManager
from src.security.interceptor import MessageSigner

class ReportAgent:
    def __init__(self):
        self.agent_name = "ReportAgent"
        self.card_manager = AgentCardManager(self.agent_name)
        self.agent_card = self.card_manager.create_agent_card(
            capabilities=["IssueHazmatComplianceVC"],
            description="Issues Verifiable Credentials for HazMat compliance."
        )
        self.signer = MessageSigner(self.agent_name)

    def issue_vc(self, scenario_id, decision, evidence_id):
        """
        Issues a Verifiable Credential (VC) for a compliance decision.
        """
        print(f"[{self.agent_name}] Issuing VC for Scenario: {scenario_id}")
        
        # Construct the VC payload (W3C style)
        vc = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/hazardsafe/v1"
            ],
            "id": f"urn:uuid:{str(uuid.uuid4())}",
            "type": ["VerifiableCredential", "HazmatComplianceCertificate"],
            "issuer": f"did:web:hazardsafe.ai:agents:{self.agent_name}",
            "issuanceDate": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "credentialSubject": {
                "id": f"urn:scenario:{scenario_id}",
                "decision": "Approved" if decision['compliant'] else "Rejected",
                "reason": decision.get('reason', 'No reason provided'),
                "evidence_root_id": evidence_id
            }
        }
        
        # Sign the VC (Proof)
        # In a real VC, this would be a Linked Data Signature or JWT.
        # We use our JWS signer for simplicity.
        proof = self.signer.sign_message(vc)
        
        vc['proof'] = {
            "type": "JsonWebSignature2020",
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"did:web:hazardsafe.ai:agents:{self.agent_name}#key-1",
            "jws": proof
        }
        
        print(f"[{self.agent_name}] VC Issued: {vc['id']}")
        return vc

if __name__ == "__main__":
    # Test
    agent = ReportAgent()
    decision = {"compliant": True, "reason": "All checks passed."}
    vc = agent.issue_vc("SCN-002", decision, "evt_123456")
    print(json.dumps(vc, indent=2))
