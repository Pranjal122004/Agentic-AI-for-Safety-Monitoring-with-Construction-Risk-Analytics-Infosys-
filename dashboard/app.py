import streamlit as st
import requests


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Construction Safety Intelligence",
    page_icon="🦺",
    layout="wide"
)


# ============================================================
# Title
# ============================================================

st.title("🦺 Construction Safety Intelligence Platform")

st.markdown(
    """
    **Agentic AI-powered construction site monitoring**

    Upload a construction-site image to detect PPE compliance
    and generate a worker safety assessment.
    """
)


# ============================================================
# FastAPI Configuration
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# API Health Check
# ============================================================

try:

    health_response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    if health_response.status_code == 200:

        st.success("🟢 Safety API is connected")

    else:

        st.warning(
            "🟡 Safety API returned an unexpected response"
        )

except requests.exceptions.RequestException:

    st.error(
        "🔴 Cannot connect to FastAPI.\n\n"
        "Start the backend with:\n\n"
        "`uvicorn backend.app.main:app --reload`"
    )


# ============================================================
# Dashboard Tabs
# ============================================================

tab1, tab2 = st.tabs(
    [
        "🦺 PPE Safety Analysis",
        "📊 Site Risk Monitoring"
    ]
)


# ============================================================
# TAB 1 — PPE SAFETY ANALYSIS
# ============================================================

with tab1:

    st.header("🦺 Worker PPE Safety Analysis")

    st.write(
        "Upload a construction-site image from the "
        "construction safety dataset."
    )

    # --------------------------------------------------------
    # Image Upload
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Choose a construction image",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )

    if uploaded_file is not None:

        # ----------------------------------------------------
        # Display Uploaded Image
        # ----------------------------------------------------

        st.image(
            uploaded_file,
            caption="Uploaded Construction Image",
            use_container_width=True
        )

        st.divider()

        # ----------------------------------------------------
        # Analyze Button
        # ----------------------------------------------------

        analyze_button = st.button(
            "🔍 Analyze PPE Safety",
            type="primary"
        )

        if analyze_button:

            with st.spinner(
                "YOLO is detecting PPE and the Safety Agent "
                "is analyzing the result..."
            ):

                try:

                    # ------------------------------------------------
                    # Prepare uploaded file
                    # ------------------------------------------------

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }

                    # ------------------------------------------------
                    # Send image to FastAPI
                    # ------------------------------------------------

                    response = requests.post(
                        f"{API_URL}/analyze-ppe",
                        files=files,
                        timeout=120
                    )

                    # =================================================
                    # SUCCESS
                    # =================================================

                    if response.status_code == 200:

                        data = response.json()

                        # ------------------------------------------------
                        # Check API error
                        # ------------------------------------------------

                        if "error" in data:

                            st.error(
                                data["error"]
                            )

                        else:

                            # =================================================
                            # Extract API response
                            # =================================================

                            safety = data.get(
                                "safety_analysis",
                                {}
                            )

                            detections = data.get(
                                "detections",
                                []
                            )

                            risk_level = safety.get(
                                "risk_level",
                                "UNKNOWN"
                            )

                            hazards = safety.get(
                                "hazards",
                                []
                            )

                            recommendations = safety.get(
                                "recommendations",
                                []
                            )

                            status = safety.get(
                                "status",
                                "No status available."
                            )

                            # =================================================
                            # SAFETY ASSESSMENT
                            # =================================================

                            st.subheader(
                                "🛡️ Safety Assessment"
                            )

                            col1, col2, col3 = st.columns(3)

                            # ------------------------------------------------
                            # Risk Level
                            # ------------------------------------------------

                            with col1:

                                st.metric(
                                    "Risk Level",
                                    risk_level
                                )

                            # ------------------------------------------------
                            # Hazards
                            # ------------------------------------------------

                            with col2:

                                st.metric(
                                    "Hazards Detected",
                                    len(hazards)
                                )

                            # ------------------------------------------------
                            # Recommendations
                            # ------------------------------------------------

                            with col3:

                                st.metric(
                                    "Recommendations",
                                    len(recommendations)
                                )

                            # =================================================
                            # RISK STATUS
                            # =================================================

                            st.subheader(
                                "🚨 Safety Status"
                            )

                            if risk_level == "LOW":

                                st.success(
                                    "🟢 LOW RISK — "
                                    "Required PPE appears compliant."
                                )

                            elif risk_level == "MEDIUM":

                                st.warning(
                                    "🟡 MEDIUM RISK — "
                                    "Preventive safety action is recommended."
                                )

                            elif risk_level == "HIGH":

                                st.error(
                                    "🔴 HIGH RISK — "
                                    "Urgent safety intervention is required."
                                )

                            elif risk_level == "CRITICAL":

                                st.error(
                                    "🚨 CRITICAL — "
                                    "Immediate intervention is required."
                                )

                            else:

                                st.warning(
                                    f"Risk level: {risk_level}"
                                )

                            # =================================================
                            # SAFETY MESSAGE
                            # =================================================

                            st.info(
                                status
                            )

                            # =================================================
                            # DETECTED OBJECTS
                            # =================================================

                            st.subheader(
                                "🔎 YOLO Detection Results"
                            )

                            if detections:

                                # Count detections by class
                                detection_counts = {}

                                for detection in detections:

                                    class_name = detection.get(
                                        "class",
                                        "Unknown"
                                    )

                                    detection_counts[class_name] = (
                                        detection_counts.get(
                                            class_name,
                                            0
                                        ) + 1
                                    )

                                # Display detection counts

                                for class_name, count in detection_counts.items():

                                    st.write(
                                        f"• **{class_name}** — "
                                        f"{count} detected"
                                    )

                            else:

                                st.warning(
                                    "No objects were detected."
                                )

                            # =================================================
                            # PPE DETECTIONS WITH CONFIDENCE
                            # =================================================

                            st.subheader(
                                "🦺 Detailed PPE Detections"
                            )

                            if detections:

                                for detection in detections:

                                    class_name = detection.get(
                                        "class",
                                        "Unknown"
                                    )

                                    confidence = detection.get(
                                        "confidence",
                                        0
                                    )

                                    confidence_percent = (
                                        confidence * 100
                                    )

                                    st.write(
                                        f"**{class_name}** — "
                                        f"{confidence_percent:.1f}% confidence"
                                    )

                            else:

                                st.write(
                                    "No detections available."
                                )

                            # =================================================
                            # HAZARDS
                            # =================================================

                            st.subheader(
                                "⚠️ Detected Hazards"
                            )

                            if hazards:

                                for hazard in hazards:

                                    st.error(
                                        f"⚠️ {hazard}"
                                    )

                            else:

                                st.success(
                                    "✅ No PPE hazards detected."
                                )

                            # =================================================
                            # RECOMMENDATIONS
                            # =================================================

                            st.subheader(
                                "🛡️ Safety Recommendations"
                            )

                            if recommendations:

                                for recommendation in recommendations:

                                    st.info(
                                        f"💡 {recommendation}"
                                    )

                            else:

                                st.success(
                                    "No additional recommendations."
                                )

                            # =================================================
                            # RAW API INFORMATION
                            # =================================================

                            with st.expander(
                                "View Technical Analysis"
                            ):

                                st.json(
                                    data
                                )

                    # =================================================
                    # API ERROR
                    # =================================================

                    else:

                        st.error(
                            f"API request failed. "
                            f"Status code: {response.status_code}"
                        )

                        try:

                            st.json(
                                response.json()
                            )

                        except Exception:

                            st.write(
                                response.text
                            )

                # =========================================================
                # CONNECTION ERROR
                # =========================================================

                except requests.exceptions.ConnectionError:

                    st.error(
                        "🔴 Could not connect to FastAPI.\n\n"
                        "Make sure the backend is running:\n\n"
                        "`uvicorn backend.app.main:app --reload`"
                    )

                # =========================================================
                # TIMEOUT ERROR
                # =========================================================

                except requests.exceptions.Timeout:

                    st.error(
                        "⏱️ The PPE analysis took too long. "
                        "Please try again."
                    )

                # =========================================================
                # OTHER ERROR
                # =========================================================

                except Exception as e:

                    st.error(
                        f"An unexpected error occurred: {str(e)}"
                    )


# ============================================================
# TAB 2 — SITE RISK MONITORING
# ============================================================

with tab2:

    st.header(
        "📊 Construction Site Risk Monitoring"
    )

    st.write(
        "Analyze environmental and equipment-related "
        "construction-site risks."
    )

    # --------------------------------------------------------
    # Analyze Site Risk Button
    # --------------------------------------------------------

    site_risk_button = st.button(
        "🔍 Analyze Site Risk",
        type="primary"
    )

    if site_risk_button:

        with st.spinner(
            "Safety Agent is analyzing site monitoring data..."
        ):

            try:

                # ------------------------------------------------
                # Call Site Risk API
                # ------------------------------------------------

                response = requests.get(
                    f"{API_URL}/site-risk",
                    timeout=30
                )

                # =================================================
                # SUCCESS
                # =================================================

                if response.status_code == 200:

                    data = response.json()

                    results = data.get(
                        "results",
                        []
                    )

                    total_records = data.get(
                        "total_records",
                        len(results)
                    )

                    # =================================================
                    # SUMMARY
                    # =================================================

                    st.subheader(
                        "📋 Site Risk Summary"
                    )

                    # ------------------------------------------------
                    # Calculate summary values
                    # ------------------------------------------------

                    if results:

                        risk_scores = [
                            result.get(
                                "risk_score",
                                0
                            )
                            for result in results
                        ]

                        average_score = (
                            sum(risk_scores)
                            / len(risk_scores)
                        )

                        highest_score = max(
                            risk_scores
                        )

                        critical_count = sum(
                            1
                            for result in results
                            if result.get(
                                "risk_level"
                            ) == "CRITICAL"
                        )

                        high_count = sum(
                            1
                            for result in results
                            if result.get(
                                "risk_level"
                            ) == "HIGH"
                        )

                    else:

                        average_score = 0
                        highest_score = 0
                        critical_count = 0
                        high_count = 0

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Monitoring Records",
                            total_records
                        )

                    with col2:

                        st.metric(
                            "Average Risk Score",
                            f"{average_score:.1f}"
                        )

                    with col3:

                        st.metric(
                            "Highest Risk Score",
                            highest_score
                        )

                    with col4:

                        st.metric(
                            "High/Critical Records",
                            high_count + critical_count
                        )

                    # =================================================
                    # SITE RISK RESULTS
                    # =================================================

                    st.subheader(
                        "📊 Risk Analysis Results"
                    )

                    if results:

                        for result in results:

                            site_id = result.get(
                                "site_id",
                                "Unknown"
                            )

                            timestamp = result.get(
                                "timestamp",
                                "Unknown"
                            )

                            risk_score = result.get(
                                "risk_score",
                                0
                            )

                            risk_level = result.get(
                                "risk_level",
                                "UNKNOWN"
                            )

                            hazards = result.get(
                                "hazards",
                                []
                            )

                            recommendation = result.get(
                                "recommendation",
                                "No recommendation."
                            )

                            # ------------------------------------------------
                            # Result container
                            # ------------------------------------------------

                            with st.container():

                                st.markdown(
                                    f"### 🏗️ {site_id}"
                                )

                                st.write(
                                    f"**Timestamp:** {timestamp}"
                                )

                                result_col1, result_col2 = st.columns(2)

                                with result_col1:

                                    st.metric(
                                        "Risk Score",
                                        f"{risk_score}/100"
                                    )

                                with result_col2:

                                    st.metric(
                                        "Risk Level",
                                        risk_level
                                    )

                                # ------------------------------------------------
                                # Risk-level message
                                # ------------------------------------------------

                                if risk_level == "CRITICAL":

                                    st.error(
                                        "🚨 CRITICAL RISK — "
                                        "Immediate action required."
                                    )

                                elif risk_level == "HIGH":

                                    st.error(
                                        "🔴 HIGH RISK — "
                                        "Urgent safety review required."
                                    )

                                elif risk_level == "MEDIUM":

                                    st.warning(
                                        "🟡 MEDIUM RISK — "
                                        "Preventive action recommended."
                                    )

                                else:

                                    st.success(
                                        "🟢 LOW RISK — "
                                        "Site conditions are acceptable."
                                    )

                                # ------------------------------------------------
                                # Hazards
                                # ------------------------------------------------

                                if hazards:

                                    st.write(
                                        "**Hazards:**"
                                    )

                                    for hazard in hazards:

                                        st.write(
                                            f"⚠️ {hazard}"
                                        )

                                else:

                                    st.write(
                                        "✅ No hazards detected."
                                    )

                                # ------------------------------------------------
                                # Recommendation
                                # ------------------------------------------------

                                st.write(
                                    "**Recommendation:**"
                                )

                                st.info(
                                    recommendation
                                )

                                st.divider()

                    else:

                        st.warning(
                            "No site monitoring records found."
                        )

                # =================================================
                # API ERROR
                # =================================================

                else:

                    st.error(
                        f"Site risk API failed. "
                        f"Status code: {response.status_code}"
                    )

                    try:

                        st.json(
                            response.json()
                        )

                    except Exception:

                        st.write(
                            response.text
                        )

            # =========================================================
            # CONNECTION ERROR
            # =========================================================

            except requests.exceptions.ConnectionError:

                st.error(
                    "🔴 Could not connect to FastAPI.\n\n"
                    "Make sure the backend is running:\n\n"
                    "`uvicorn backend.app.main:app --reload`"
                )

            # =========================================================
            # TIMEOUT ERROR
            # =========================================================

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ Site risk analysis timed out."
                )

            # =========================================================
            # OTHER ERROR
            # =========================================================

            except Exception as e:

                st.error(
                    f"An unexpected error occurred: {str(e)}"
                )