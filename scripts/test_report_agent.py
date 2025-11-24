from src.agents.report_agent import ReportAgent

def test_report_agent():
    print("Initializing ReportAgent...")
    agent = ReportAgent()
    
    # Simulate a decision from Compliance Agent
    decision = {
        "compliant": True, 
        "reason": "Ambient temperature 25C is < 38C limit."
    }
    
    print("\n--- Issuing VC ---")
    vc = agent.issue_vc("SCN-TEST-001", decision, "evt_mock_provenance_id")
    
    if vc and vc['credentialSubject']['decision'] == "Approved":
        print("✅ VC Issued Successfully.")
        print(f"VC ID: {vc['id']}")
        print(f"Proof: {vc['proof']['jws'][:20]}...")
    else:
        print("❌ Failed to issue VC.")

if __name__ == "__main__":
    test_report_agent()
