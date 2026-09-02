from fastapi import FastAPI
from backend.app.agents.site_risk_agent import SiteRiskAgent


app = FastAPI(
    title="Construction Risk Intelligence Platform",
    description="Agentic AI-powered construction site risk monitoring system",
    version="1.0.0"
)

agent = SiteRiskAgent()


@app.get("/")
def home():
    return {
        "message": "Construction Risk Intelligence Platform is running",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/site-risk")
def get_site_risk():

    data_file = "backend/data/site_monitoring.csv"

    results = agent.analyze_dataset(data_file)

    return {
        "total_records": len(results),
        "results": results
    }