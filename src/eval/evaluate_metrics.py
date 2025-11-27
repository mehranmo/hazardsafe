import random
import time
from src.agents.compliance_agent import HazardComplianceAgent

class Evaluator:
    def __init__(self):
        self.agent = HazardComplianceAgent()
        
    def generate_test_set(self, size=50):
        """Generate synthetic test cases with ground truth"""
        dataset = []
        for _ in range(size):
            # 50% chance of being compliant (temp <= 38)
            is_compliant = random.choice([True, False])
            
            if is_compliant:
                temp = random.uniform(20.0, 38.0)
            else:
                temp = random.uniform(38.1, 60.0)
                
            scenario = {
                "material_class": "Class 7",
                "package_type": "Type B(U)",
                "ambient_temperature_c": round(temp, 1),
                "transport_index": round(random.uniform(0.1, 1.0), 2),
                "expected_result": is_compliant
            }
            dataset.append(scenario)
        return dataset

    def run_evaluation(self, dataset):
        """Run evaluation on the dataset"""
        results = {
            "total": len(dataset),
            "correct": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "errors": 0,
            "latency_ms": []
        }
        
        print(f"🧪 Starting evaluation on {len(dataset)} scenarios...")
        
        for i, case in enumerate(dataset):
            start_time = time.time()
            try:
                decision = self.agent.check_scenario(case)
                latency = (time.time() - start_time) * 1000
                results["latency_ms"].append(latency)
                
                predicted = decision.get("compliant", False)
                expected = case["expected_result"]
                
                if predicted == expected:
                    results["correct"] += 1
                elif predicted and not expected:
                    results["false_positives"] += 1
                    print(f"   ❌ False Positive at index {i}: Temp {case['ambient_temperature_c']}C")
                elif not predicted and expected:
                    results["false_negatives"] += 1
                    print(f"   ❌ False Negative at index {i}: Temp {case['ambient_temperature_c']}C")
                    
            except Exception as e:
                results["errors"] += 1
                print(f"   ⚠️ Error at index {i}: {e}")
                
        # Calculate metrics
        results["accuracy"] = (results["correct"] / results["total"]) * 100
        results["avg_latency"] = sum(results["latency_ms"]) / len(results["latency_ms"]) if results["latency_ms"] else 0
        
        return results

if __name__ == "__main__":
    evaluator = Evaluator()
    dataset = evaluator.generate_test_set(size=20)
    metrics = evaluator.run_evaluation(dataset)
    
    print("\n" + "="*40)
    print("📊 Evaluation Results")
    print("="*40)
    print(f"Accuracy:        {metrics['accuracy']:.1f}%")
    print(f"Total Samples:   {metrics['total']}")
    print(f"False Positives: {metrics['false_positives']}")
    print(f"False Negatives: {metrics['false_negatives']}")
    print(f"Avg Latency:     {metrics['avg_latency']:.1f} ms")
    print("="*40)
