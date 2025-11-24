#!/usr/bin/env python3
"""
Test runner for HazardSAFE scenarios.
Loads scenarios from data/test_scenarios.json and runs them through the compliance agent.
"""

import json
import sys
import os

# Ensure PYTHONPATH is set
sys.path.insert(0, '/home/mmonavar/Projects/aqi/aqi')
os.environ['PYTHONPATH'] = '/home/mmonavar/Projects/aqi/aqi'

from src.agents.compliance_agent import HazardComplianceAgent

def run_scenario_tests():
    print("\n" + "="*70)
    print("  HazardSAFE Scenario Test Suite")
    print("="*70 + "\n")
    
    # Load scenarios
    with open('data/test_scenarios.json', 'r') as f:
        scenarios = json.load(f)
    
    # Initialize agent
    agent = HazardComplianceAgent()
    
    # Track results
    results = {
        'total': len(scenarios),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # Run each scenario
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n[{idx}/{len(scenarios)}] Testing: {scenario['name']}")
        print(f"     ID: {scenario['id']}")
        print(f"     Description: {scenario['description']}")
        print(f"     Temperature: {scenario['ambient_temperature_c']}°C")
        
        # Run compliance check
        decision = agent.check_scenario(scenario)
        
        # Compare with expected result
        actual_compliant = decision['compliant']
        expected_compliant = scenario['expected_result'] == 'compliant'
        
        test_passed = actual_compliant == expected_compliant
        
        if test_passed:
            results['passed'] += 1
            status = "✅ PASS"
        else:
            results['failed'] += 1
            status = "❌ FAIL"
        
        print(f"     Expected: {'Compliant' if expected_compliant else 'Non-compliant'}")
        print(f"     Actual:   {'Compliant' if actual_compliant else 'Non-compliant'}")
        print(f"     Reason: {decision['reason']}")
        print(f"     Result: {status}")
        
        results['details'].append({
            'scenario_id': scenario['id'],
            'name': scenario['name'],
            'expected': scenario['expected_result'],
            'actual': 'compliant' if actual_compliant else 'non-compliant',
            'passed': test_passed,
            'reason': decision['reason']
        })
    
    # Print summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"  Total Tests:  {results['total']}")
    print(f"  Passed:       {results['passed']} ✅")
    print(f"  Failed:       {results['failed']} ❌")
    
    pass_rate = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
    print(f"  Pass Rate:    {pass_rate:.1f}%")
    print("="*70 + "\n")
    
    # Save detailed results
    with open('data/test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Detailed results saved to: data/test_results.json\n")
    
    return results['failed'] == 0

if __name__ == "__main__":
    success = run_scenario_tests()
    sys.exit(0 if success else 1)
