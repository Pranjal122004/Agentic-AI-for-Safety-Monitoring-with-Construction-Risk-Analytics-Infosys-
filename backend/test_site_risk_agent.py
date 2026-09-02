from app.agents.site_risk_agent import SiteRiskAgent


agent = SiteRiskAgent()

data_file = "backend/data/site_monitoring.csv"

results = agent.analyze_dataset(data_file)

for result in results:
    print("=" * 60)
    print(f"Site: {result['site_id']}")
    print(f"Time: {result['timestamp']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Hazards: {result['hazards']}")
    print(f"Recommendation: {result['recommendation']}")
    