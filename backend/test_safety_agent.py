from app.agents.safety_agent import SafetyAgent


agent = SafetyAgent()

data_file = "data/worker_monitoring.csv"

results = agent.analyze_dataset(data_file)


for result in results:

    print("=" * 60)

    print(f"Site: {result['site_id']}")
    print(f"Worker: {result['worker_id']}")
    print(f"Time: {result['timestamp']}")
    print(f"Safety Score: {result['safety_score']}")
    print(f"Safety Level: {result['safety_level']}")
    print(f"PPE Violations: {result['ppe_violations']}")
    print(f"Unsafe Behavior: {result['unsafe_behavior']}")
    print(f"Alert: {result['alert']}")
