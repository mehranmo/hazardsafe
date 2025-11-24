import json
from src.eval.red_team_agent import RedTeamAgent
from src.agents.compliance_agent import HazardComplianceAgent

def run_evaluation():
    print("--- Starting Adversarial Evaluation ---")
    
    red_team = RedTeamAgent()
    compliance_agent = HazardComplianceAgent() # Will use Mock Mode if API fails
    
    # Generate Scenarios
    scenarios = red_team.generate_adversarial_scenarios(count=5)
    
    results = {
        "total": 0,
        "passed_check": 0, # Agent successfully made a decision (even if rejection)
        "crashed": 0,
        "details": []
    }
    
    for scn in scenarios:
        results["total"] += 1
        print(f"\nTesting Scenario: {scn['id']} ({scn.get('description', '')})")
        print(f"Data: {scn}")
        
        try:
            decision = compliance_agent.check_scenario(scn)
            print(f"Decision: {decision['compliant']} | Reason: {decision['reason']}")
            
            results["passed_check"] += 1
            results["details"].append({
                "scenario_id": scn['id'],
                "outcome": "Decision Made",
                "compliant": decision['compliant'],
                "reason": decision['reason']
            })
            
        except Exception as e:
            print(f"CRASHED: {e}")
            results["crashed"] += 1
            results["details"].append({
                "scenario_id": scn['id'],
                "outcome": "Crashed",
                "error": str(e)
            })

    print("\n--- Evaluation Summary ---")
    print(f"Total Scenarios: {results['total']}")
    print(f"Decisions Made: {results['passed_check']}")
    print(f"Crashes: {results['crashed']}")
    
    # Simple robustness score
    score = (results['passed_check'] / results['total']) * 100 if results['total'] > 0 else 0
    print(f"Robustness Score: {score}%")

if __name__ == "__main__":
    run_evaluation()
