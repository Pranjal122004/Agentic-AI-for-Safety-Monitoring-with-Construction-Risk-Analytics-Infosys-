from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File

from backend.app.agents.site_risk_agent import SiteRiskAgent
from backend.app.agents.safety_agent import SafetyAgent
from backend.app.services.ppe_detector import PPEDetector


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

MODEL_PATH = PROJECT_ROOT / "models" / "ppe_model.pt"

UPLOAD_DIR = PROJECT_ROOT / "uploads"


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Construction Risk Intelligence Platform",
    description=(
        "Agentic AI-powered construction site risk monitoring "
        "and worker safety platform"
    ),
    version="2.0.0"
)


# ============================================================
# Agents
# ============================================================

site_risk_agent = SiteRiskAgent()

safety_agent = SafetyAgent()


# ============================================================
# PPE Detector
# ============================================================

ppe_detector = None

if MODEL_PATH.exists():
    ppe_detector = PPEDetector(str(MODEL_PATH))


# ============================================================
# Home Endpoint
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Construction Risk Intelligence Platform is running",
        "status": "active"
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# Site Risk Endpoint
# ============================================================

@app.get("/site-risk")
def get_site_risk():

    data_file = DATA_DIR / "site_monitoring.csv"

    results = site_risk_agent.analyze_dataset(
        str(data_file)
    )

    return {
        "total_records": len(results),
        "results": results
    }


# ============================================================
# Worker Safety Endpoint
# ============================================================

@app.get("/safety-risk")
def get_safety_risk():

    data_file = DATA_DIR / "worker_monitoring.csv"

    results = safety_agent.analyze_dataset(
        str(data_file)
    )

    return {
        "total_workers": len(results),
        "results": results
    }


# ============================================================
# PPE Image Analysis Endpoint
# ============================================================

@app.post("/analyze-ppe")
async def analyze_ppe(
    file: UploadFile = File(...)
):

    # Check whether model exists
    if ppe_detector is None:

        return {
            "error": "PPE model not found.",
            "expected_model": str(MODEL_PATH)
        }

    # Create uploads folder
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Keep only the filename
    safe_filename = Path(file.filename).name

    file_path = UPLOAD_DIR / safe_filename

    # Save uploaded image
    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Run YOLO PPE detection
    detections = ppe_detector.detect(
        str(file_path)
    )

    # Analyze PPE detections
    safety_result = safety_agent.analyze_detections(
        detections
    )

    return {
        "filename": safe_filename,
        "detections": detections,
        "safety_analysis": safety_result
    }