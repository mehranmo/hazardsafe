import json
from src.security.agent_card import AgentCardManager

class MessageSigner:
    def __init__(self, agent_name, secret_key=None):
        self.card_manager = AgentCardManager(agent_name, private_key=secret_key)

    def sign_message(self, message_dict):
        """
        Wraps a message payload in a JWS signature.
        """
        # We treat the whole message dict as the payload
        signed_token = self.card_manager.create_agent_card(
            capabilities=[], # Not used for message signing, just reusing the JWS logic
            description=json.dumps(message_dict) # Embedding message in description field is a hack for this demo class
            # In a real implementation, we'd use a proper JWS payload structure: { "msg": ... }
        )
        
        # Let's do it properly with the underlying library if possible, 
        # but reusing the manager is faster for this prototype.
        # Actually, let's just use the manager's key to sign a custom payload.
        
        payload = {
            "iss": self.card_manager.agent_name,
            "msg": message_dict
        }
        # We access the internal secret (in prod use a proper signer class)
        from jose import jws, constants
        signed = jws.sign(payload, self.card_manager.secret, algorithm=constants.ALGORITHMS.HS256)
        return signed

    def verify_message(self, signed_message):
        """
        Verifies JWS and returns the original message dict.
        """
        from jose import jws, constants
        try:
            # In a real system, we'd look up the sender's public key based on 'iss' header.
            # Here we assume shared secret for demo simplicity.
            payload = jws.verify(signed_message, self.card_manager.secret, algorithms=[constants.ALGORITHMS.HS256])
            data = json.loads(payload)
            return data['msg']
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return None
