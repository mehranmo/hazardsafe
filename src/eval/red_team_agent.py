import os
import json
import random
import google.generativeai as genai
from src.security.agent_card import AgentCardManager

class RedTeamAgent:
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        self.agent_name = "RedTeamAgent"
        self.card_manager = AgentCardManager(self.agent_name)
        
        # Configure Gemini
        if "GOOGLE_API_KEY" not in os.environ:
             print("WARNING: GOOGLE_API_KEY not found. RedTeamAgent using heuristic generation.")
             self.mock_mode = True
        else:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.model = genai.GenerativeModel(model_name)
            self.mock_mode = False # Set to True if API is flaky

    def generate_adversarial_scenarios(self, count=3):
        """
        Generates tricky scenarios to test the Compliance Agent.
        """
        print(f"[{self.agent_name}] Generating {count} adversarial scenarios...")
        
        scenarios = []
        
        if self.mock_mode:
            # Heuristic generation of edge cases
            for i in range(count):
                # Edge case: Temperature exactly at the limit or slightly above
                temp = 38 + random.choice([-0.1, 0.0, 0.1, 5.0])
                scenarios.append({
                    "id": f"ADV-MOCK-{i}",
                    "material_class": "Class 7",
                    "package_type": "Type B(U)",
                    "ambient_temperature_c": round(temp, 1),
                    "transport_index": 0.5,
                    "description": "Adversarial temperature test"
                })
        else:
            prompt = f"""
            You are a Red Team Agent testing a Hazardous Material Compliance System.
            Generate {count} JSON scenarios that are tricky, borderline, or malicious to test the system's robustness.
            Focus on:
            1. Temperatures near the 38C limit.
            2. Ambiguous material classes.
            3. Missing fields (though our schema validator might catch this, it's good to test).
            
            Output a JSON list of objects. Each object should have:
            - id (string)
            - material_class (string)
            - package_type (string)
            - ambient_temperature_c (number)
            - transport_index (number)
            - description (string explaining why it is tricky)
            
            Output ONLY the JSON list.
            """
            
            try:
                response = self.model.generate_content(prompt)
                text = response.text.replace("```json", "").replace("```", "").strip()
                scenarios = json.loads(text)
            except Exception as e:
                print(f"[{self.agent_name}] LLM Generation failed: {e}. Falling back to heuristics.")
                # Fallback
                return self.generate_adversarial_scenarios(count)

        return scenarios

if __name__ == "__main__":
    agent = RedTeamAgent()
    scenarios = agent.generate_adversarial_scenarios(2)
    print(json.dumps(scenarios, indent=2))
