import json
import time
from jose import jws, jwt
from jose.constants import ALGORITHMS

# In a real production system, keys would be managed by a KMS or Secret Manager.
# For this prototype/Kaggle env, we will generate/load keys locally.

class AgentCardManager:
    def __init__(self, agent_name, private_key=None, public_key=None):
        self.agent_name = agent_name
        # For demo purposes, if no keys provided, we generate a symmetric key (HS256) 
        # or we could generate RSA keys. 
        # Let's use HS256 with a hardcoded secret for simplicity in this demo, 
        # BUT we acknowledge this should be RSA/ECDSA in prod.
        self.secret = private_key or "super-secret-demo-key-for-hazardsafe" 
        
    def create_agent_card(self, capabilities, description):
        """
        Creates a Signed Agent Card (JWS).
        """
        payload = {
            "iss": "hazardsafe-authority", # Issuer
            "sub": self.agent_name,        # Subject (Agent Name)
            "iat": int(time.time()),       # Issued At
            "exp": int(time.time()) + 3600*24, # Expires in 24h
            "card": {
                "name": self.agent_name,
                "description": description,
                "capabilities": capabilities, # List of tool names or A2A ops
                "version": "1.0.0"
            }
        }
        
        # Sign the payload
        signed_card = jws.sign(payload, self.secret, algorithm=ALGORITHMS.HS256)
        return signed_card

    def verify_agent_card(self, signed_card):
        """
        Verifies a Signed Agent Card and returns the payload.
        """
        try:
            payload = jws.verify(signed_card, self.secret, algorithms=[ALGORITHMS.HS256])
            return json.loads(payload)
        except Exception as e:
            print(f"Verification failed: {e}")
            return None

if __name__ == "__main__":
    # Test
    mgr = AgentCardManager("ComplianceAgent")
    card = mgr.create_agent_card(["CheckHazmatScenario"], "Ensures regulatory compliance.")
    print(f"Signed Card: {card}")
    
    decoded = mgr.verify_agent_card(card)
    print(f"Verified: {decoded}")
