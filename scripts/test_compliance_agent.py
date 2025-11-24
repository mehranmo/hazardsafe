import os
from src.agents.compliance_agent import HazardComplianceAgent

def test_agent():
    print("Initializing HazardComplianceAgent...")
    try:
        agent = HazardComplianceAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        return

    # Scenario 1: Non-Compliant (High Temp)
    scenario_fail = {
        "id": "SCN-001",
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 45, 
        "transport_index": 0.5
    }
    
    print(f"\n--- Testing Scenario 1 (Should FAIL) ---\n{scenario_fail}")
    decision = agent.check_scenario(scenario_fail)
    print(f"Decision: {decision['compliant']}")
    print(f"Reason: {decision['reason']}")
    
    if decision['compliant'] == False:
        print("✅ Correctly rejected.")
    else:
        print("❌ Failed to reject.")

    # Scenario 2: Compliant
    scenario_pass = {
        "id": "SCN-002",
        "material_class": "Class 7",
        "package_type": "Type B(U)",
        "ambient_temperature_c": 25, 
        "transport_index": 0.5
    }
    
    print(f"\n--- Testing Scenario 2 (Should PASS) ---\n{scenario_pass}")
    decision = agent.check_scenario(scenario_pass)
    print(f"Decision: {decision['compliant']}")
    print(f"Reason: {decision['reason']}")

    if decision['compliant'] == True:
        print("✅ Correctly approved.")
    else:
        print("❌ Failed to approve.")

if __name__ == "__main__":
    # We allow running without API key now, as the agent will switch to Mock Mode.
    test_agent()
