from pathlib import Path
import shutil
import base64
from datetime import datetime

from fastapi import FastAPI, UploadFile, File

from backend.app.agents.site_risk_agent import SiteRiskAgent
from backend.app.agents.safety_agent import SafetyAgent
from backend.app.services.ppe_detector import PPEDetector
from backend.app.agents.compliance_agent import ComplianceAgent
from backend.app.agents.insurance_agent import InsuranceAgent


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
        "AI-powered construction site risk monitoring "
        "and worker safety platform"
    ),
    version="2.1.0"
)


# ============================================================
# Agents
# ============================================================

site_risk_agent = SiteRiskAgent()

safety_agent = SafetyAgent()

compliance_agent = ComplianceAgent()

insurance_agent = InsuranceAgent()


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
        "message": (
            "Construction Risk Intelligence Platform is running"
        ),
        "status": "active",
        "version": "2.1.0"
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "ppe_model_loaded": ppe_detector is not None
    }


# ============================================================
# Site Risk Endpoint
# ============================================================

@app.get("/site-risk")
def get_site_risk():

    data_file = DATA_DIR / "site_monitoring.csv"

    if not data_file.exists():

        return {
            "error": "Site monitoring data file not found.",
            "expected_file": str(data_file)
        }

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

    if not data_file.exists():

        return {
            "error": "Worker monitoring data file not found.",
            "expected_file": str(data_file)
        }

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

    # --------------------------------------------------------
    # 1. Check PPE model
    # --------------------------------------------------------

    if ppe_detector is None:

        return {
            "error": "PPE model not found.",
            "expected_model": str(MODEL_PATH)
        }

    # --------------------------------------------------------
    # 2. Create uploads folder
    # --------------------------------------------------------

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 3. Keep only filename
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    # --------------------------------------------------------
    # 4. Save uploaded image
    # --------------------------------------------------------

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # --------------------------------------------------------
    # 5. Run YOLO PPE detection
    # --------------------------------------------------------

    detections = ppe_detector.detect(
        str(file_path)
    )

    # --------------------------------------------------------
    # 6. Analyze PPE detections
    # --------------------------------------------------------

    safety_result = safety_agent.analyze_detections(
        detections
    )

    # --------------------------------------------------------
    # 7. Reliability summary
    # --------------------------------------------------------

    high_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "HIGH"
    )

    review_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "REVIEW"
    )

    low_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "LOW"
    )

    return {

        "analysis_timestamp":
            datetime.now().isoformat(),

        "filename":
            safe_filename,

        "detections":
            detections,

        "reliability_summary": {

            "total_detections":
                len(detections),

            "high_confidence_detections":
                high_confidence_count,

            "review_required_detections":
                review_count,

            "low_confidence_detections":
                low_confidence_count,

            "manual_review_required":
                review_count > 0
        },

        "safety_analysis":
            safety_result
    }


# ============================================================
# Combined Safety Analysis - GET
# ============================================================

@app.get("/combined-safety-analysis")
def combined_safety_analysis_get():

    # --------------------------------------------------------
    # 1. Load site monitoring data
    # --------------------------------------------------------

    data_file = DATA_DIR / "site_monitoring.csv"

    if not data_file.exists():

        return {
            "error": "Site monitoring data file not found."
        }

    site_results = site_risk_agent.analyze_dataset(
        str(data_file)
    )

    # --------------------------------------------------------
    # 2. Select latest site result
    # --------------------------------------------------------

    if not site_results:

        return {
            "error": "No site monitoring data found."
        }

    latest_site_result = site_results[-1]

    # --------------------------------------------------------
    # 3. No image provided
    # --------------------------------------------------------

    ppe_result = {
        "detections": []
    }

    # --------------------------------------------------------
    # 4. Run Safety Agent
    # --------------------------------------------------------

    combined_result = safety_agent.analyze(
        ppe_result,
        latest_site_result
    )

    # --------------------------------------------------------
    # 5. Return result
    # --------------------------------------------------------

    return {

        "analysis_timestamp":
            datetime.now().isoformat(),

        "site_analysis":
            latest_site_result,

        "combined_safety_analysis":
            combined_result
    }


# ============================================================
# Combined PPE + Site Risk Analysis
# ============================================================

@app.post("/combined-safety-analysis")
async def combined_safety_analysis_post(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # 1. Check PPE model
    # --------------------------------------------------------

    if ppe_detector is None:

        return {
            "error": "PPE model not found.",
            "expected_model": str(MODEL_PATH)
        }

    # --------------------------------------------------------
    # 2. Create upload directory
    # --------------------------------------------------------

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 3. Save uploaded image
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # --------------------------------------------------------
    # 4. Run PPE detection
    # --------------------------------------------------------

    detections = ppe_detector.detect(
        str(file_path)
    )

    ppe_result = {
        "detections": detections
    }

    # --------------------------------------------------------
    # 5. Load site monitoring data
    # --------------------------------------------------------

    data_file = DATA_DIR / "site_monitoring.csv"

    if not data_file.exists():

        return {
            "error": "Site monitoring data file not found."
        }

    site_results = site_risk_agent.analyze_dataset(
        str(data_file)
    )

    if not site_results:

        return {
            "error": "No site monitoring data found."
        }

    # --------------------------------------------------------
    # 6. Use latest site result
    # --------------------------------------------------------

    latest_site_result = site_results[-1]

    # --------------------------------------------------------
    # 7. Run combined Safety Agent
    # --------------------------------------------------------

    combined_result = safety_agent.analyze(
        ppe_result,
        latest_site_result
    )

    # --------------------------------------------------------
    # 8. Reliability summary
    # --------------------------------------------------------

    high_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "HIGH"
    )

    review_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "REVIEW"
    )

    low_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "LOW"
    )

    # --------------------------------------------------------
    # 9. Return result
    # --------------------------------------------------------

    return {

        "analysis_timestamp":
            datetime.now().isoformat(),

        "filename":
            safe_filename,

        "ppe_detections":
            detections,

        "reliability_summary": {

            "total_detections":
                len(detections),

            "high_confidence_detections":
                high_confidence_count,

            "review_required_detections":
                review_count,

            "low_confidence_detections":
                low_confidence_count,

            "manual_review_required":
                review_count > 0
        },

        "site_analysis":
            latest_site_result,

        "combined_safety_analysis":
            combined_result
    }


# ============================================================
# Compliance Analysis Endpoint
# ============================================================

@app.post("/analyze-compliance")
async def analyze_compliance(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # 1. Check PPE model
    # --------------------------------------------------------

    if ppe_detector is None:

        return {
            "error": "PPE model not found.",
            "expected_model": str(MODEL_PATH)
        }

    # --------------------------------------------------------
    # 2. Create uploads folder
    # --------------------------------------------------------

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 3. Save image
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # --------------------------------------------------------
    # 4. Run PPE detection
    # --------------------------------------------------------

    detections = ppe_detector.detect(
        str(file_path)
    )

    # --------------------------------------------------------
    # 5. Prepare PPE result
    # --------------------------------------------------------

    ppe_result = {

        "filename":
            safe_filename,

        "detections":
            detections
    }

    # --------------------------------------------------------
    # 6. Run Compliance Agent
    # --------------------------------------------------------

    compliance_result = compliance_agent.analyze(
        ppe_result
    )

    # --------------------------------------------------------
    # 7. Reliability summary
    # --------------------------------------------------------

    high_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "HIGH"
    )

    review_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "REVIEW"
    )

    low_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "LOW"
    )

    # --------------------------------------------------------
    # 8. Return result
    # --------------------------------------------------------

    return {

        "analysis_timestamp":
            datetime.now().isoformat(),

        "filename":
            safe_filename,

        "detections":
            detections,

        "reliability_summary": {

            "total_detections":
                len(detections),

            "high_confidence_detections":
                high_confidence_count,

            "review_required_detections":
                review_count,

            "low_confidence_detections":
                low_confidence_count,

            "manual_review_required":
                review_count > 0
                or compliance_result.get(
                    "total_reviews",
                    0
                ) > 0
        },

        "compliance_analysis":
            compliance_result
    }


# ============================================================
# COMPLETE RISK ANALYSIS
# PPE + SAFETY + COMPLIANCE + SITE RISK + INSURANCE
# ============================================================

@app.post("/analyze-risk")
async def analyze_risk(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # 1. Check PPE model
    # --------------------------------------------------------

    if ppe_detector is None:

        return {
            "error": "PPE model not found.",
            "expected_model": str(MODEL_PATH)
        }

    # --------------------------------------------------------
    # 2. Create uploads folder
    # --------------------------------------------------------

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 3. Save uploaded image
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # --------------------------------------------------------
    # --------------------------------------------------------
    # 4. PPE DETECTION + ANNOTATED IMAGE
    # --------------------------------------------------------

    detection_result = ppe_detector.detect_and_annotate(
        str(file_path)
    )

    detections = detection_result["detections"]

    annotated_path = Path(
        detection_result["annotated_image"]
    )

    with open(annotated_path, "rb") as image_file:
        annotated_image_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    ppe_result = {
        "filename": safe_filename,
        "detections": detections
    }

    # --------------------------------------------------------
    # 5. SAFETY ANALYSIS
    # --------------------------------------------------------

    safety_result = safety_agent.analyze_detections(
        detections
    )

    ppe_result["safety_analysis"] = safety_result

    # --------------------------------------------------------
    # 6. COMPLIANCE ANALYSIS
    # --------------------------------------------------------

    compliance_result = compliance_agent.analyze(
        ppe_result
    )

    # --------------------------------------------------------
    # 7. SITE RISK ANALYSIS
    # --------------------------------------------------------

    data_file = DATA_DIR / "site_monitoring.csv"

    if not data_file.exists():

        return {
            "error": "Site monitoring data file not found."
        }

    site_results = site_risk_agent.analyze_dataset(
        str(data_file)
    )

    if not site_results:

        return {
            "error": "No site monitoring data found."
        }

    # Use latest site monitoring record
    latest_site_result = site_results[-1]

    # --------------------------------------------------------
    # 8. INSURANCE RISK ANALYSIS
    # --------------------------------------------------------

    insurance_result = insurance_agent.assess_risk(
        ppe_result=ppe_result,
        site_risk_result=latest_site_result,
        compliance_result=compliance_result
    )

    # --------------------------------------------------------
    # 9. CLAIM RISK
    # --------------------------------------------------------

    claim_risk = insurance_agent.assess_claim_risk(
        insurance_result
    )

    # --------------------------------------------------------
    # 10. RELIABILITY SUMMARY
    # --------------------------------------------------------

    high_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "HIGH"
    )

    review_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "REVIEW"
    )

    low_confidence_count = sum(
        1
        for detection in detections
        if detection.get(
            "confidence_level"
        ) == "LOW"
    )

    manual_review_required = (
        review_count > 0
        or compliance_result.get(
            "total_reviews",
            0
        ) > 0
        or insurance_result.get(
            "manual_review_required",
            False
        )
    )

    # --------------------------------------------------------
    # 11. FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "analysis_timestamp":
            datetime.now().isoformat(),

        "filename":
            safe_filename,

        "detections":
            detections,

        "annotated_image_base64":
            annotated_image_base64,

        "reliability_summary": {

            "total_detections":
                len(detections),

            "high_confidence_detections":
                high_confidence_count,

            "review_required_detections":
                review_count,

            "low_confidence_detections":
                low_confidence_count,

            "manual_review_required":
                manual_review_required
        },

        "safety_analysis":
            safety_result,

        "compliance_analysis":
            compliance_result,

        "site_analysis":
            latest_site_result,

        "insurance_analysis": {

            **insurance_result,

            "claim_risk":
                claim_risk
        }
    }