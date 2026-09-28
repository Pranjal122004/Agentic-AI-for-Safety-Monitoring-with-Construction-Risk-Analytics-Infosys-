import base64
from io import BytesIO
from datetime import datetime

import requests
import streamlit as st
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

# ============================================================
# Page setup
# ============================================================
st.set_page_config(
    page_title="SiteGuard AI | Construction Risk Intelligence",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://127.0.0.1:8000"
ANALYZE_URL = f"{API_BASE}/analyze-risk"
HEALTH_URL = f"{API_BASE}/health"
SITE_RISK_URL = f"{API_BASE}/site-risk"
RISK_INTELLIGENCE_URL = f"{API_BASE}/risk-intelligence"
REPORT_URL = f"{API_BASE}/generate-report"
ORCHESTRATION_URL = f"{API_BASE}/agent-orchestration"

# ============================================================
# Theme / styling
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root { --bg:#0b1020; --panel:#121a2d; --panel2:#172239; --line:#26334d;
            --text:#edf3ff; --muted:#9aabc7; --cyan:#53d8e8; --green:#4ade80;
            --amber:#fbbf24; --red:#fb7185; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(ellipse at top left, #172746 0%, #0b1020 45%, #080d18 100%); color:var(--text); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#10192c,#0b1020); border-right:1px solid #25324a; }
    [data-testid="stSidebar"] * { color:#eaf1ff; }
    h1,h2,h3 { color:#f4f7ff !important; letter-spacing:-.035em; }
    p, label, li { color:#c6d2e8; }
    .hero { padding:26px 28px; border:1px solid #2a3b58; border-radius:22px;
            background:linear-gradient(115deg,rgba(28,48,79,.95),rgba(17,27,47,.88));
            box-shadow:0 18px 55px rgba(0,0,0,.22); margin-bottom:22px;
            animation:rise .55s ease-out both; }
    .eyebrow { color:#6ee7f2; font-size:12px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
    .hero-title { font-size:clamp(27px,3.4vw,42px); line-height:1.12; font-weight:800; margin:8px 0; color:#f7faff; }
    .hero-sub { color:#aebed7; font-size:15px; max-width:760px; }
    .metric { background:linear-gradient(145deg,#17243b,#111a2c); border:1px solid #293955;
              border-radius:17px; padding:17px 18px; min-height:112px;
              transition:transform .18s ease,border-color .18s ease; }
    .metric:hover { transform:translateY(-3px); border-color:#53d8e8; }
    .metric-label { color:#9aabc7; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
    .metric-value { color:#f4f8ff; font-size:29px; font-weight:800; margin-top:8px; }
    .metric-note { color:#93a7c7; font-size:12px; margin-top:2px; }
    .section-card { background:rgba(18,26,45,.88); border:1px solid #263650; border-radius:18px; padding:20px; }
    .pill { display:inline-block; padding:5px 10px; border-radius:99px; font-size:11px; font-weight:800;
            letter-spacing:.07em; background:#1c3448; color:#7ce8f1; border:1px solid #31556a; }
    div.stButton > button { border-radius:12px; min-height:44px; font-weight:700;
        border:1px solid #344762; background:linear-gradient(135deg,#1b2d48,#142238); color:#eff7ff;
        transition:all .18s ease; }
    div.stButton > button:hover { border-color:#53d8e8; color:#fff; transform:translateY(-1px); }
    [data-testid="stFileUploader"] { background:#111b2e; border:1px dashed #3a5274; border-radius:16px; padding:14px; }
    [data-testid="stFileUploader"] * { color:#eaf1ff !important; }
    [data-testid="stFileUploaderDropzone"] { background:#17243a !important; border-radius:12px !important; }
    [data-testid="stDataFrame"] { border:1px solid #293955; border-radius:12px; overflow:hidden; }
    [data-testid="stTabs"] button { color:#b7c6df; font-weight:700; }
    [data-testid="stTabs"] button[aria-selected="true"] { color:#6ee7f2; }
    .small-muted { color:#93a7c7; font-size:12px; }
    @keyframes rise { from { opacity:0; transform:translateY(9px); } to { opacity:1; transform:translateY(0); } }
    @media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Helpers
# ============================================================
def safe_get(data, *keys, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pretty_json(value):
    st.json(value if value is not None else {"message": "No data available"})


def call_health():
    try:
        response = requests.get(HEALTH_URL, timeout=4)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def get_site_risk():
    try:
        response = requests.get(SITE_RISK_URL, timeout=12)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def run_analysis(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    try:
        response = requests.post(ANALYZE_URL, files=files, timeout=180)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict) and result.get("error"):
            return None, result["error"]
        return result, None
    except requests.Timeout:
        return None, "The analysis took too long. Try a smaller image or check the backend terminal."
    except requests.RequestException as exc:
        return None, f"Could not reach the backend API: {exc}"

def run_orchestration(ppe_result, site_risk_result):
    payload = {
        "ppe_result": ppe_result,
        "site_risk_result": site_risk_result,
    }

    try:
        response = requests.post(
            ORCHESTRATION_URL,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json(), None

    except requests.Timeout:
        return None, "Agent orchestration took too long."

    except requests.RequestException as exc:
        return None, f"Agent orchestration failed: {exc}"


def detection_frame(detections):
    if not isinstance(detections, list) or not detections:
        return pd.DataFrame(columns=["Class", "Confidence", "Reliability", "Bounding box"])
    rows = []
    for item in detections:
        if not isinstance(item, dict):
            continue
        rows.append({
            "Class": item.get("class", "Unknown"),
            "Confidence": item.get("confidence", None),
            "Reliability": item.get("confidence_level", "N/A"),
            "Bounding box": item.get("bbox", item.get("box", "—")),
        })
    return pd.DataFrame(rows)


def section_heading(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


def create_pdf_report(report):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    story = [
        Paragraph("Construction Site Risk Report", title_style),
        Spacer(1, 15),
        Paragraph(
            f"<b>Generated:</b> {report.get('generated_at', 'N/A')}",
            normal_style,
        ),
        Spacer(1, 15),
    ]

    story.append(Paragraph("Executive Summary", heading_style))
    story.append(
        Paragraph(
            str(report.get("summary", "No summary available.")),
            normal_style,
        )
    )
    story.append(Spacer(1, 15))

    risk = report.get("risk_intelligence", {})
    story.append(Paragraph("Risk Intelligence", heading_style))
    risk_items = [
        ("Site", risk.get("site_id", "N/A")),
        ("Risk Score", risk.get("risk_score", "N/A")),
        ("Risk Level", risk.get("risk_level", "N/A")),
        ("Total Hazards", risk.get("total_hazards", 0)),
        (
            "Manual Review",
            "Required" if risk.get("manual_review_required") else "Not Required",
        ),
    ]
    for label, value in risk_items:
        story.append(Paragraph(f"<b>{label}:</b> {value}", normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Recommendations", heading_style))
    recommendations = risk.get("recommendations", [])
    if recommendations:
        for item in recommendations:
            story.append(Paragraph(f"• {item}", normal_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No recommendations available.", normal_style))
    story.append(Spacer(1, 15))

    safety = report.get("safety", {})
    reliability = safety.get("reliability_summary", {})
    story.append(Paragraph("Safety Analysis", heading_style))
    safety_items = [
        ("Total PPE Detections", reliability.get("total_detections", 0)),
        ("High Confidence", reliability.get("high_confidence_detections", 0)),
        ("Review Required", reliability.get("review_required_detections", 0)),
        ("Low Confidence", reliability.get("low_confidence_detections", 0)),
    ]
    for label, value in safety_items:
        story.append(Paragraph(f"<b>{label}:</b> {value}", normal_style))
    story.append(Spacer(1, 15))

    site_risk = report.get("site_risk", {})
    if site_risk:
        story.append(Paragraph("Site Risk", heading_style))
        for label, key in [
            ("Site ID", "site_id"),
            ("Risk Score", "risk_score"),
            ("Risk Level", "risk_level"),
            ("Recommendation", "recommendation"),
        ]:
            if key in site_risk:
                story.append(Paragraph(f"<b>{label}:</b> {site_risk.get(key)}", normal_style))
        story.append(Spacer(1, 15))

    compliance = report.get("compliance", {})
    if compliance:
        story.append(Paragraph("Compliance", heading_style))
        for key, value in compliance.items():
            if not isinstance(value, (dict, list)):
                story.append(
                    Paragraph(
                        f"<b>{str(key).replace('_', ' ').title()}:</b> {value}",
                        normal_style,
                    )
                )
        story.append(Spacer(1, 15))

    insurance = report.get("insurance", {})
    if insurance:
        story.append(Paragraph("Insurance", heading_style))
        for key, value in insurance.items():
            if not isinstance(value, (dict, list)):
                story.append(
                    Paragraph(
                        f"<b>{str(key).replace('_', ' ').title()}:</b> {value}",
                        normal_style,
                    )
                )
        story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated by SiteGuard AI · Construction Risk Intelligence Platform",
            normal_style,
        )
    )

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# Sidebar navigation
# ============================================================
with st.sidebar:
    st.markdown("## 🦺 SiteGuard **AI**")
    st.caption("Construction Risk Intelligence")
    st.divider()
    page = st.radio(
        "NAVIGATION",
        [
            "Command Center",
            "AI Vision Lab",
            "Safety Review",
            "Risk Intelligence",
            "Compliance",
            "Site Risk",
            "Insurance",
            "Alerts & Reports",
        ],
        label_visibility="visible",
    )
    st.divider()
    health, health_error = call_health()
    if health:
        model_loaded = health.get("ppe_model_loaded", False)
        st.markdown("**Backend status**")
        st.success("API connected" if health.get("status") == "healthy" else "API responding")
        st.caption("PPE model: " + ("Loaded" if model_loaded else "Not loaded"))
    else:
        st.markdown("**Backend status**")
        st.error("API unavailable")
        st.caption("Start FastAPI, then refresh this page.")
    st.divider()
    st.caption("Local development • FastAPI + Streamlit")

# Shared analysis result state
if "risk_result" not in st.session_state:
    st.session_state.risk_result = None

if "orchestration_result" not in st.session_state:
    st.session_state.orchestration_result = None

if "last_upload_name" not in st.session_state:
    st.session_state.last_upload_name = None

result = st.session_state.risk_result
orchestration = st.session_state.orchestration_result
detections = safe_get(result, "detections", default=[]) if result else []
summary = safe_get(result, "reliability_summary", default={}) if result else {}
safety = safe_get(result, "safety_analysis", default={}) if result else {}
compliance = safe_get(result, "compliance_analysis", default={}) if result else {}
site = safe_get(result, "site_analysis", default={}) if result else {}
insurance = safe_get(result, "insurance_analysis", default={}) if result else {}
claim_risk = safe_get(insurance, "claim_risk", default={}) if insurance else {}

# ============================================================
# Shared hero
# ============================================================
st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">AI-powered construction safety</div>
      <div class="hero-title">{"Command Center" if page == "Command Center" else page}</div>
      <div class="hero-sub">A unified workspace for PPE detection, safety review, site conditions,
      compliance signals, and insurance risk context.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Command Center
# ============================================================
if page == "Command Center":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("PPE detections", summary.get("total_detections", "—"), "From latest image analysis")
    with col2:
        metric_card("High confidence", summary.get("high_confidence_detections", "—"), "Model confidence ≥ 80%")
    with col3:
        metric_card("Needs review", summary.get("review_required_detections", "—"), "Review medium-confidence results")
    with col4:
        manual = summary.get("manual_review_required")
        metric_card("Manual review", "Required" if manual else ("No" if manual is False else "—"), "Based on available analysis")

    st.markdown("")
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        section_heading("Start an inspection", "Upload a site image to run the complete backend risk-analysis pipeline.")
        uploaded = st.file_uploader(
            "Choose a construction-site image",
            type=["jpg", "jpeg", "png", "webp"],
            key="command_upload",
            help="Use a clear image showing workers and their PPE.",
        )
        if uploaded:
            st.image(uploaded, caption=f"Selected: {uploaded.name}", use_container_width=True)
        if st.button("▶  Analyze site image", type="primary", use_container_width=True):

            with st.spinner("Running complete AI agent workflow…"):

                new_result, error = run_analysis(uploaded)
   
            if error:
                st.error(error)

            else:
                st.session_state.risk_result = new_result
                st.session_state.last_upload_name = uploaded.name

                ppe_result = {
                    "detections": new_result.get("detections", [])
                }

                site_risk_result = new_result.get(
                    "site_analysis",
                    {}
                )

                orchestration_result, orchestration_error = run_orchestration(
                    ppe_result,
                    site_risk_result
                )

                if orchestration_error:
                    st.warning(
                        f"Image analysis completed, but orchestration failed: "
                        f"{orchestration_error}"
                    )
                else:
                    st.session_state.orchestration_result = orchestration_result
                    st.success(
                        "Complete AI agent workflow finished successfully."
                    )

                st.rerun()  
    with right:
        section_heading("Latest inspection", "This panel updates after a successful image analysis.")
        if result:
            st.markdown(f'<span class="pill">ANALYSIS READY</span>', unsafe_allow_html=True)
            st.write(f"**Image:** {st.session_state.last_upload_name or result.get('filename', 'Uploaded image')}")
            st.write(f"**Timestamp:** {result.get('analysis_timestamp', 'Not provided')}")
            st.write(f"**Detections:** {summary.get('total_detections', len(detections))}")
            st.write(f"**Manual review:** {'Required' if summary.get('manual_review_required') else 'Not flagged'}")
            st.info("Use AI Vision Lab and the review pages to inspect the detailed findings.")
        else:
            st.info("No image has been analyzed in this session yet.")
            st.caption("Your existing API endpoints remain the source of analysis results.")

# ============================================================
# AI Vision Lab
# ============================================================
elif page == "AI Vision Lab":
    section_heading("Image inspection", "Upload an image and inspect YOLO detections, confidence, and annotated output.")
    uploaded = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "webp"],
        key="vision_upload",
    )
    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        if uploaded:
            st.image(uploaded, caption="Original image", use_container_width=True)
    with col_b:
        if uploaded and st.button("Run AI vision analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing image…"):
                new_result, error = run_analysis(uploaded)
            if error:
                st.error(error)
            else:
                st.session_state.risk_result = new_result
                st.session_state.last_upload_name = uploaded.name
                st.success("Vision analysis complete.")
                st.rerun()

    if result:
        st.divider()
        section_heading("Annotated detection output", "Bounding boxes appear here when the API returns an annotated image.")
        encoded = result.get("annotated_image_base64")
        if encoded:
            try:
                image_bytes = base64.b64decode(encoded)
                st.image(BytesIO(image_bytes), caption="YOLO annotated image", use_container_width=True)
            except (ValueError, TypeError):
                st.warning("The annotated image payload could not be decoded.")
        else:
            st.info("The current API response does not include `annotated_image_base64`. Check that the updated main.py is running.")
        df = detection_frame(detections)
        section_heading("Detected objects")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty and "Class" in df:
            st.bar_chart(df["Class"].value_counts(), use_container_width=True)

# ============================================================
# Safety Review
# ============================================================
elif page == "Safety Review":
    section_heading(
        "Safety Review",
        "Human-readable safety findings from the AI Safety Agent."
    )

    if not result:
        st.info(
            "Run an image analysis from Command Center or AI Vision Lab first."
        )
    else:

        # ----------------------------------------------------
        # Safety status
        # ----------------------------------------------------
        safety_risk = safety.get("risk_level", "UNKNOWN")
        safety_status = safety.get(
            "status",
            "No safety status was returned."
        )

        confirmed_violations = safety.get(
            "confirmed_violations",
            0
        )

        review_required = safety.get(
            "review_required",
            0
        )

        hazards = safety.get(
            "hazards",
            []
        )

        recommendations = safety.get(
            "recommendations",
            []
        )

        # ----------------------------------------------------
        # Main safety metrics
        # ----------------------------------------------------
        a, b, c, d = st.columns(4)

        with a:
            metric_card(
                "Safety Risk",
                safety_risk,
                "Current safety assessment"
            )

        with b:
            metric_card(
                "PPE Detections",
                summary.get(
                    "total_detections",
                    len(detections)
                ),
                "Objects detected in the image"
            )

        with c:
            metric_card(
                "Confirmed Violations",
                confirmed_violations,
                "High-confidence safety violations"
            )

        with d:
            metric_card(
                "Review Required",
                review_required,
                "Findings requiring verification"
            )

        st.markdown("")

        # ----------------------------------------------------
        # Safety status message
        # ----------------------------------------------------
        st.markdown("### Safety Status")

        if confirmed_violations > 0:
            st.error(
                f"{confirmed_violations} confirmed safety violation(s) "
                "were detected. Immediate site verification is recommended."
            )
        elif review_required > 0:
            st.warning(
                f"{review_required} finding(s) require additional review "
                "before the result can be treated as confirmed."
            )
        else:
            st.success(
                "No high-confidence PPE safety violation was detected."
            )

        st.info(safety_status)

        # ----------------------------------------------------
        # Detected PPE and objects
        # ----------------------------------------------------
        st.markdown("### Detected Safety Equipment and Objects")

        df = detection_frame(detections)

        if not df.empty:

            # Remove technical bounding-box information
            # from the dashboard.
            display_df = df[
                ["Class", "Confidence", "Reliability"]
            ].copy()

            display_df["Confidence"] = display_df[
                "Confidence"
            ].apply(
                lambda x: f"{float(x) * 100:.1f}%"
                if x is not None
                else "—"
            )

            display_df.columns = [
                "Detected Item",
                "Confidence",
                "Detection Reliability"
            ]

            confidence_filter = st.selectbox(
                "Show detections",
                [
                    "All",
                    "HIGH",
                    "REVIEW",
                    "LOW"
                ]
            )

            if confidence_filter != "All":
                display_df = display_df[
                    display_df["Detection Reliability"]
                    == confidence_filter
                ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "No PPE or safety objects were detected in this image."
            )

        # ----------------------------------------------------
        # Safety hazards
        # ----------------------------------------------------
        st.markdown("### Safety Hazards")

        if hazards:
            for hazard in hazards:
                st.warning(str(hazard))
        else:
            st.success(
                "No specific safety hazards were reported by the Safety Agent."
            )

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------
        st.markdown("### Recommended Actions")

        if recommendations:
            for recommendation in recommendations:
                st.write(
                    "• " + str(recommendation)
                )
        else:
            st.info(
                "No additional safety actions were recommended."
            )

        # ----------------------------------------------------
        # Review note
        # ----------------------------------------------------
        st.markdown("")
        st.caption(
            "AI findings are decision-support information. "
            "Site personnel should verify safety conditions physically."
        )

# ============================================================
# Risk Intelligence
# ============================================================
elif page == "Risk Intelligence":
    section_heading(
        "Construction Risk Intelligence",
        "Combines site-risk and safety findings into one operational summary.",
    )

    if not result:
        st.info("Run an image analysis first from the Command Center.")
    else:
        payload = {
            "site_risk_result": site,
            "safety_result": safety,
        }

        try:
            response = requests.post(
                RISK_INTELLIGENCE_URL,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            intelligence = response.json()

            st.success("Risk Intelligence generated successfully.")

            a, b, c, d = st.columns(4)
            with a:
                metric_card(
                    "Risk Score",
                    intelligence.get("risk_score", "—"),
                    "Overall site risk score",
                )
            with b:
                metric_card(
                    "Risk Level",
                    intelligence.get("risk_level", "—"),
                    "Current site risk level",
                )
            with c:
                metric_card(
                    "Total Hazards",
                    intelligence.get("total_hazards", 0),
                    "Detected hazards",
                )
            with d:
                metric_card(
                    "Manual Review",
                    "Required" if intelligence.get("manual_review_required") else "Not Required",
                    "Based on uncertain detections",
                )

            st.markdown("### Risk Summary")
            st.info(intelligence.get("summary", "No summary available."))

            st.markdown("### Hazards")
            hazards = intelligence.get("hazards", [])
            if hazards:
                for hazard in hazards:
                    st.warning(str(hazard))
            else:
                st.success("No hazards detected.")

            st.markdown("### Recommendations")
            recommendations = intelligence.get("recommendations", [])
            if recommendations:
                for recommendation in recommendations:
                    st.write("• " + str(recommendation))
            else:
                st.info("No recommendations available.")

        except requests.RequestException as exc:
            st.error(f"Could not load Risk Intelligence: {exc}")

# ============================================================
# Compliance
# ============================================================
elif page == "Compliance":

    section_heading(
        "Compliance Review",
        "A simple summary of PPE and safety compliance findings."
    )

    if not result:
        st.info(
            "Run an image analysis from the Command Center first."
        )

    else:

        compliance_status = compliance.get(
            "compliance_status",
            "Not Available"
        )

        total_violations = compliance.get(
            "total_violations",
            0
        )

        total_reviews = compliance.get(
            "total_reviews",
            0
        )

        violations = compliance.get(
            "violations",
            []
        )

        review_findings = compliance.get(
            "review_findings",
            []
        )

        recommendations = compliance.get(
            "recommendations",
            []
        )

        # ----------------------------------------------------
        # Compliance summary
        # ----------------------------------------------------

        a, b, c = st.columns(3)

        with a:
            metric_card(
                "Compliance Status",
                compliance_status,
                "Current safety compliance"
            )

        with b:
            metric_card(
                "Violations",
                total_violations,
                "Confirmed compliance issues"
            )

        with c:
            metric_card(
                "Items for Review",
                total_reviews,
                "Findings requiring verification"
            )

        st.markdown("")

        # ----------------------------------------------------
        # Status message
        # ----------------------------------------------------

        if compliance_status == "COMPLIANT":

            st.success(
                "The analyzed site image does not show any confirmed "
                "PPE compliance violations."
            )

        elif compliance_status == "NON-COMPLIANT":

            st.error(
                "The analyzed site image contains confirmed "
                "PPE compliance violations."
            )

        else:

            st.warning(
                "The compliance status requires additional review."
            )

        # ----------------------------------------------------
        # Violations
        # ----------------------------------------------------

        st.markdown("### Compliance Findings")

        if violations:

            for violation in violations:
                st.warning(
                    f"⚠️ {str(violation)}"
                )

        else:

            st.success(
                "No confirmed compliance violations were identified."
            )

        # ----------------------------------------------------
        # Review findings
        # ----------------------------------------------------

        st.markdown("### Items Requiring Review")

        if review_findings:

            for finding in review_findings:
                st.info(
                    f"🔎 {str(finding)}"
                )

        else:

            st.write(
                "No additional compliance review items were identified."
            )

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        st.markdown("### Recommendations")

        if recommendations:

            for recommendation in recommendations:
                st.write(
                    f"• {str(recommendation)}"
                )

        else:

            st.write(
                "Continue following standard construction-site "
                "safety procedures and PPE requirements."
            )

        # ----------------------------------------------------
        # Human-readable report
        # ----------------------------------------------------

        st.markdown("### Compliance Report")

        compliance_report_text = f"""
        Construction Site Compliance Report

        Compliance Status: {compliance_status}

        Confirmed Violations: {total_violations}

        Items Requiring Review: {total_reviews}

        """

        if violations:
            compliance_report_text += "\nConfirmed Findings:\n"
            for violation in violations:
                compliance_report_text += f"- {violation}\n"
        else:
            compliance_report_text += (
                "\nConfirmed Findings:\n"
                "- No confirmed compliance violations identified.\n"
            )

        if review_findings:
            compliance_report_text += "\nItems Requiring Review:\n"
            for finding in review_findings:
                compliance_report_text += f"- {finding}\n"

        if recommendations:
            compliance_report_text += "\nRecommendations:\n"
            for recommendation in recommendations:
                compliance_report_text += f"- {recommendation}\n"

        # ----------------------------------------------------
        # PDF generation
        # ----------------------------------------------------

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        heading_style = styles["Heading2"]
        normal_style = styles["BodyText"]

        story = [
            Paragraph(
                "Construction Site Compliance Report",
                title_style
            ),
            Spacer(1, 20),

            Paragraph(
                f"<b>Compliance Status:</b> "
                f"{compliance_status}",
                normal_style
            ),
            Spacer(1, 8),

            Paragraph(
                f"<b>Confirmed Violations:</b> "
                f"{total_violations}",
                normal_style
            ),
            Spacer(1, 8),

            Paragraph(
                f"<b>Items Requiring Review:</b> "
                f"{total_reviews}",
                normal_style
            ),
            Spacer(1, 20),

            Paragraph(
                "Compliance Findings",
                heading_style
            ),
        ]

        if violations:

            for violation in violations:
                story.append(
                    Paragraph(
                        f"• {str(violation)}",
                        normal_style
                    )
                )
                story.append(Spacer(1, 5))

        else:

            story.append(
                Paragraph(
                    "No confirmed compliance violations were identified.",
                    normal_style
                )
            )

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "Items Requiring Review",
                heading_style
            )
        )

        if review_findings:

            for finding in review_findings:
                story.append(
                    Paragraph(
                        f"• {str(finding)}",
                        normal_style
                    )
                )
                story.append(Spacer(1, 5))

        else:

            story.append(
                Paragraph(
                    "No additional review items were identified.",
                    normal_style
                )
            )

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "Recommendations",
                heading_style
            )
        )

        if recommendations:

            for recommendation in recommendations:
                story.append(
                    Paragraph(
                        f"• {str(recommendation)}",
                        normal_style
                    )
                )
                story.append(Spacer(1, 5))

        else:

            story.append(
                Paragraph(
                    "Continue following standard construction-site "
                    "safety procedures and PPE requirements.",
                    normal_style
                )
            )

        story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                "Generated by SiteGuard AI - "
                "Construction Risk Intelligence Platform",
                normal_style
            )
        )

        document.build(story)

        buffer.seek(0)

        st.download_button(
            "⬇ Download Compliance Report (PDF)",
            data=buffer.getvalue(),
            file_name="construction_compliance_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ============================================================
# Site Risk
# ============================================================
elif page == "Site Risk":
    section_heading(
        "Site Risk",
        "Monitor environmental conditions and the current construction-site risk level."
    )

    site_data, site_error = get_site_risk()

    if site_error:
        st.error(
            f"Could not load site-risk information: {site_error}"
        )

    elif site_data:

        rows = site_data.get("results", [])

        if not rows:
            st.info(
                "No site monitoring records are currently available."
            )

        else:

            # ------------------------------------------------
            # Latest site record
            # ------------------------------------------------
            latest = rows[-1]

            site_id = latest.get(
                "site_id",
                site.get("site_id", "Unknown")
            )

            timestamp = latest.get(
                "timestamp",
                "Not available"
            )

            temperature = latest.get(
                "temperature",
                None
            )

            humidity = latest.get(
                "humidity",
                None
            )

            dust_level = latest.get(
                "dust_level",
                None
            )

            noise_level = latest.get(
                "noise_level",
                None
            )

            equipment_status = latest.get(
                "equipment_status",
                "Not available"
            )

            worker_count = latest.get(
                "worker_count",
                "Not available"
            )

            unsafe_condition = latest.get(
                "unsafe_condition",
                "Not available"
            )

            # Use the risk result from the latest image analysis
            risk_score = site.get(
                "risk_score",
                "—"
            ) if site else "—"

            risk_level = site.get(
                "risk_level",
                "—"
            ) if site else "—"

            # ------------------------------------------------
            # Site overview
            # ------------------------------------------------
            st.markdown("### Current Site Overview")

            a, b, c, d = st.columns(4)

            with a:
                metric_card(
                    "Site",
                    site_id,
                    "Current monitoring location"
                )

            with b:
                metric_card(
                    "Risk Score",
                    risk_score,
                    "Overall site risk"
                )

            with c:
                metric_card(
                    "Risk Level",
                    risk_level,
                    "Current assessment"
                )

            with d:
                metric_card(
                    "Workers",
                    worker_count,
                    "Workers recorded on site"
                )

            st.markdown("")

            # ------------------------------------------------
            # Environmental conditions
            # ------------------------------------------------
            st.markdown("### Environmental Conditions")

            e1, e2, e3, e4 = st.columns(4)

            with e1:
                value = (
                    f"{temperature}°C"
                    if temperature is not None
                    else "—"
                )
                metric_card(
                    "Temperature",
                    value,
                    "Recorded site temperature"
                )

            with e2:
                value = (
                    f"{humidity}%"
                    if humidity is not None
                    else "—"
                )
                metric_card(
                    "Humidity",
                    value,
                    "Recorded humidity"
                )

            with e3:
                metric_card(
                    "Dust Level",
                    dust_level if dust_level is not None else "—",
                    "Recorded dust level"
                )

            with e4:
                metric_card(
                    "Noise Level",
                    noise_level if noise_level is not None else "—",
                    "Recorded noise level"
                )

            # ------------------------------------------------
            # Operational conditions
            # ------------------------------------------------
            st.markdown("### Operational Conditions")

            op1, op2 = st.columns(2)

            with op1:
                st.markdown("#### Equipment Status")

                if str(equipment_status).lower() == "faulty":
                    st.error(
                        "⚠ Equipment requires attention."
                    )
                elif str(equipment_status).lower() == "normal":
                    st.success(
                        "✓ Equipment status is normal."
                    )
                else:
                    st.info(
                        f"Equipment status: {equipment_status}"
                    )

            with op2:
                st.markdown("#### Unsafe Condition")

                if str(unsafe_condition).lower() == "yes":
                    st.warning(
                        "⚠ An unsafe site condition was recorded."
                    )
                elif str(unsafe_condition).lower() == "no":
                    st.success(
                        "✓ No unsafe condition was recorded."
                    )
                else:
                    st.info(
                        f"Unsafe condition: {unsafe_condition}"
                    )

            # ------------------------------------------------
            # Latest monitoring time
            # ------------------------------------------------
            st.markdown("### Latest Monitoring Record")

            st.info(
                f"Site **{site_id}** was last monitored at "
                f"**{timestamp}**."
            )

            # ------------------------------------------------
            # Risk recommendation
            # ------------------------------------------------
            if site:
                recommendation = site.get(
                    "recommendation"
                )

                if recommendation:
                    st.markdown("### Recommended Action")
                    st.info(str(recommendation))

                hazards = site.get(
                    "hazards",
                    []
                )

                st.markdown("### Site Hazards")

                if hazards:
                    for hazard in hazards:
                        st.warning(str(hazard))
                else:
                    st.success(
                        "No specific site hazards were reported."
                    )

            # ------------------------------------------------
            # Historical monitoring
            # ------------------------------------------------
            if len(rows) > 1:
                st.markdown("### Monitoring History")

                history_rows = []

                for row in rows:
                    history_rows.append({
                        "Time": row.get(
                            "timestamp",
                            "—"
                        ),
                        "Temperature": (
                            f"{row.get('temperature')}°C"
                            if row.get("temperature") is not None
                            else "—"
                        ),
                        "Humidity": (
                            f"{row.get('humidity')}%"
                            if row.get("humidity") is not None
                            else "—"
                        ),
                        "Dust": row.get(
                            "dust_level",
                            "—"
                        ),
                        "Noise": row.get(
                            "noise_level",
                            "—"
                        ),
                        "Equipment": row.get(
                            "equipment_status",
                            "—"
                        ),
                        "Unsafe Condition": row.get(
                            "unsafe_condition",
                            "—"
                        ),
                    })

                history_df = pd.DataFrame(history_rows)

                st.dataframe(
                    history_df,
                    use_container_width=True,
                    hide_index=True
                )

            st.caption(
                "Site-risk information is based on the project's "
                "site monitoring records and latest risk analysis."
            )

    else:
        st.info(
            "No site-risk information was returned by the backend."
        )

# ============================================================
# Insurance
# ============================================================
elif page == "Insurance":
    section_heading(
        "Insurance Risk",
        "Understand how current safety and site conditions may affect insurance exposure."
    )

    if not result:
        st.info("Run an image analysis first.")

    else:

        # ----------------------------------------------------
        # Insurance information
        # ----------------------------------------------------
        insurance_data = insurance if isinstance(
            insurance,
            dict
        ) else {}

        claim_data = claim_risk if isinstance(
            claim_risk,
            dict
        ) else {}

        # Support different names returned by the backend
        risk_level = insurance_data.get(
            "risk_level",
            insurance_data.get(
                "overall_risk",
                "Not available"
            )
        )

        premium_adjustment = insurance_data.get(
            "premium_adjustment",
            "Not available"
        )

        # ----------------------------------------------------
        # Main insurance overview
        # ----------------------------------------------------
        st.markdown("### Insurance Overview")

        a, b, c = st.columns(3)

        with a:
            metric_card(
                "Insurance Risk",
                risk_level,
                "Current insurance exposure"
            )

        with b:
            metric_card(
                "Premium Impact",
                premium_adjustment,
                "Adjustment reported by the agent"
            )

        with c:

            claim_level = claim_data.get(
                "risk_level",
                claim_data.get(
                    "claim_risk",
                    "Not available"
                )
            )

            metric_card(
                "Claim Risk",
                claim_level,
                "Potential claim exposure"
            )

        st.markdown("")

        # ----------------------------------------------------
        # Risk message
        # ----------------------------------------------------
        st.markdown("### Risk Assessment")

        risk_text = str(
            risk_level
        ).upper()

        if risk_text in [
            "HIGH",
            "CRITICAL",
            "VERY HIGH"
        ]:
            st.error(
                "The current site conditions indicate elevated "
                "insurance exposure. Site conditions should be "
                "reviewed promptly."
            )

        elif risk_text in [
            "MEDIUM",
            "MODERATE"
        ]:
            st.warning(
                "The current site conditions indicate moderate "
                "insurance exposure. Continue monitoring and "
                "address identified risks."
            )

        elif risk_text == "LOW":
            st.success(
                "The current site conditions indicate relatively "
                "low insurance exposure."
            )

        else:
            st.info(
                "The Insurance Agent did not return a clear "
                "risk classification."
            )

        # ----------------------------------------------------
        # Insurance factors
        # ----------------------------------------------------
        st.markdown("### Factors Considered")

        factors = []

        if site:
            site_level = site.get(
                "risk_level"
            )

            if site_level:
                factors.append(
                    f"Site risk level: {site_level}"
                )

            site_score = site.get(
                "risk_score"
            )

            if site_score is not None:
                factors.append(
                    f"Site risk score: {site_score}"
                )

        if safety:
            safety_level = safety.get(
                "risk_level"
            )

            if safety_level:
                factors.append(
                    f"Worker safety risk level: {safety_level}"
                )

        if compliance:
            total_reviews = compliance.get(
                "total_reviews"
            )

            if total_reviews is not None:
                factors.append(
                    f"Compliance items requiring review: {total_reviews}"
                )

        if summary:
            manual_review = summary.get(
                "manual_review_required",
                False
            )

            factors.append(
                "Manual verification required: "
                + ("Yes" if manual_review else "No")
            )

        if factors:

            for factor in factors:
                st.write(
                    "• " + str(factor)
                )

        else:
            st.info(
                "No additional insurance risk factors were returned."
            )

        # ----------------------------------------------------
        # Claim risk details
        # ----------------------------------------------------
        if claim_data:

            st.markdown("### Claim Risk Assessment")

            claim_message = (
                claim_data.get("recommendation")
                or claim_data.get("summary")
                or claim_data.get("message")
            )

            if claim_message:
                st.info(
                    str(claim_message)
                )

            claim_factors = (
                claim_data.get("risk_factors")
                or claim_data.get("factors")
                or []
            )

            if claim_factors:

                st.markdown("#### Claim Risk Factors")

                if isinstance(
                    claim_factors,
                    list
                ):
                    for factor in claim_factors:
                        st.write(
                            "• " + str(factor)
                        )

                else:
                    st.write(
                        str(claim_factors)
                    )

        # ----------------------------------------------------
        # Recommended action
        # ----------------------------------------------------
        st.markdown("### Recommended Action")

        recommendation = (
            insurance_data.get(
                "recommendation"
            )
            or insurance_data.get(
                "recommended_action"
            )
            or insurance_data.get(
                "action"
            )
        )

        if recommendation:

            st.info(
                str(recommendation)
            )

        else:

            if risk_text in [
                "HIGH",
                "CRITICAL",
                "VERY HIGH"
            ]:
                st.warning(
                    "Review the identified site and safety risks "
                    "before continuing normal operations."
                )

            elif risk_text in [
                "MEDIUM",
                "MODERATE"
            ]:
                st.info(
                    "Continue monitoring site conditions and "
                    "address outstanding safety or compliance issues."
                )

            else:
                st.success(
                    "Continue regular monitoring and maintain "
                    "current safety controls."
                )

        st.caption(
            "Insurance information is AI-generated decision support "
            "and should be reviewed with appropriate insurance and "
            "site-management professionals."
        )

# ============================================================
# Alerts & Reports
# ============================================================
elif page == "Alerts & Reports":
    section_heading(
        "Alerts & Reports",
        "Review current alerts and generate a professional PDF report.",
    )

    if not result:
        st.info("Run an image analysis first.")
    else:
        if summary.get("manual_review_required"):
            st.warning(
                "Manual review is flagged by the returned analysis. "
                "A qualified person should verify the site findings."
            )
        else:
            st.success("The returned summary does not flag manual review.")

        a, b = st.columns(2)
        with a:
            st.write(
                f"**Source image:** "
                f"{result.get('filename', st.session_state.last_upload_name or '—')}"
            )
        with b:
            st.write(
                f"**Analysis time:** "
                f"{result.get('analysis_timestamp', '—')}"
            )

        report_payload = {
            "site_risk_result": site,
            "safety_result": safety,
            "compliance_result": compliance,
            "insurance_result": insurance,
        }

        try:
            response = requests.post(
                REPORT_URL,
                json=report_payload,
                timeout=30,
            )
            response.raise_for_status()
            report = response.json()

            st.success("Automated report generated successfully.")

            st.markdown("### Report Summary")
            st.info(
                report.get(
                    "summary",
                    "No report summary available.",
                )
            )

            risk_intelligence = report.get(
                "risk_intelligence",
                {},
            )

            if risk_intelligence:
                st.markdown("### Risk Intelligence")

                a, b, c, d = st.columns(4)
                with a:
                    metric_card(
                        "Risk Score",
                        risk_intelligence.get("risk_score", "—"),
                        "Site risk score",
                    )
                with b:
                    metric_card(
                        "Risk Level",
                        risk_intelligence.get("risk_level", "—"),
                        "Current risk level",
                    )
                with c:
                    metric_card(
                        "Hazards",
                        risk_intelligence.get("total_hazards", 0),
                        "Detected hazards",
                    )
                with d:
                    metric_card(
                        "Manual Review",
                        "Required" if risk_intelligence.get("manual_review_required") else "Not Required",
                        "Review status",
                    )

                st.markdown("### Recommendations")
                recommendations = risk_intelligence.get("recommendations", [])
                if recommendations:
                    for recommendation in recommendations:
                        st.write("• " + str(recommendation))
                else:
                    st.info("No recommendations available.")

            pdf_data = create_pdf_report(report)

            st.markdown("### Download Report")
            st.download_button(
                "⬇ Download Professional PDF Report",
                data=pdf_data,
                file_name="construction_risk_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.caption(
                "The report is provided as a professional PDF. "
                "Raw JSON is not displayed on this page."
            )

        except requests.RequestException as exc:
            st.error(f"Could not generate report: {exc}")

st.markdown(
    '<div class="small-muted" style="text-align:center;padding:26px 0 10px;">SiteGuard AI • Decision support only — verify findings on site.</div>',
    unsafe_allow_html=True,
)
