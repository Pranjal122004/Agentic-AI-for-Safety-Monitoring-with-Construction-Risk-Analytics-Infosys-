import streamlit as st
import requests


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Construction Safety Intelligence",
    page_icon="🏗️",
    layout="wide"
)


# ============================================================
# Title
# ============================================================

st.title("🏗️ Construction Safety Intelligence Platform")

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
        st.warning("🟡 Safety API returned an unexpected response")

except requests.exceptions.RequestException:

    st.error(
        "🔴 Cannot connect to FastAPI. "
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
# TAB 1 — PPE SAFETY
# ============================================================

with tab1:

    st.header("🦺 Worker PPE Safety Analysis")

    st.write(
        "Upload a construction-site image from the Kaggle "
        "construction safety dataset."
    )

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
        # Display uploaded image
        # ----------------------------------------------------

        st.image(
            uploaded_file,
            caption="Uploaded Construction Image",
            use_container_width=True
        )

        st.divider()

        analyze_button = st.button(
            "🔍 Analyze PPE Safety",
            type="primary"
        )

        if analyze_button:

            with st.spinner(
                "YOLO is detecting PPE and the Safety Agent is analyzing the result..."
            ):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/analyze-ppe",
                        files=files,
                        timeout=120
                    )

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

                            safety = data.get(
                                "safety_analysis",
                                {}
                            )

                            detections = data.get(
                                "detections",
                                []
                            )

                            # ============================================
                            # SAFETY SUMMARY
                            # ============================================

                            st.subheader(
                                "Safety Assessment"
                            )

                            score = safety.get(
                                "safety_score",
                                0
                            )

                            level = safety.get(
                                "safety_level",
                                "UNKNOWN"
                            )

                            violations = safety.get(
                                "violations",
                                []
                            )

                            alert = safety.get(
                                "alert",
                                "No alert available."
                            )

                            col1, col2, col3 = st.columns(3)

                            with col1:

                                st.metric(
                                    "Safety Score",
                                    f"{score}/100"
                                )

                            with col2:

                                st.metric(
                                    "Safety Level",
                                    level
                                )

                            with col3:

                                st.metric(
                                    "Violations",
                                    len(violations)
                                )

                            # ============================================
                            # SAFETY STATUS
                            # ============================================

                            if level == "SAFE":

                                st.success(
                                    "🟢 SAFE — "
                                    "Worker PPE compliance is satisfactory."
                                )

                            elif level == "MODERATE":

                                st.warning(
                                    "🟡 MODERATE — "
                                    "PPE compliance should be improved."
                                )

                            elif level == "HIGH RISK":

                                st.error(
                                    "🟠 HIGH RISK — "
                                    "Urgent safety action is required."
                                )

                            else:

                                st.error(
                                    "🔴 CRITICAL — "
                                    "Immediate intervention is required."
                                )

                            # ============================================
                            # ALERT
                            # ============================================

                            st.subheader(
                                "🚨 Safety Alert"
                            )

                            st.info(
                                alert
                            )

                            # ============================================
                            # DETECTED PPE
                            # ============================================

                            st.subheader(
                                "🦺 Detected PPE"
                            )

                            detected_ppe = safety.get(
                                "detected_ppe",
                                []
                            )

                            if detected_ppe:

                                for item in detected_ppe:

                                    st.write(
                                        f"✅ {item}"
                                    )

                            else:

                                st.write(
                                    "No compliant PPE detected."
                                )

                            # ============================================
                            # VIOLATIONS
                            # ============================================

                            st.subheader(
                                "⚠️ PPE Violations"
                            )

                            if violations:

                                for violation in violations:

                                    st.error(
                                        f"❌ {violation}"
                                    )

                            else:

                                st.success(
                                    "No PPE violations detected."
                                )

                            # ============================================
                            # YOLO DETECTIONS
                            # ============================================

                            st.subheader(
                                "🔎 YOLO Detection Results"
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

                                    st.write(
                                        f"**{class_name}** — "
                                        f"confidence: {confidence:.3f}"
                                    )

                            else:

                                st.warning(
                                    "No objects were detected."
                                )

                    else:

                        st.error(
                            f"FastAPI returned HTTP "
                            f"{response.status_code}"
                        )

                        st.code(
                            response.text
                        )

                except requests.exceptions.RequestException as error:

                    st.error(
                        "Could not connect to the Safety API."
                    )

                    st.code(
                        str(error)
                    )


# ============================================================
# TAB 2 — SITE RISK
# ============================================================

with tab2:

    st.header("📊 Construction Site Risk Monitoring")

    st.write(
        "View risk analysis generated by the Site Risk Agent."
    )

    if st.button(
        "🔄 Load Site Risk Data"
    ):

        try:

            response = requests.get(
                f"{API_URL}/site-risk",
                timeout=30
            )

            if response.status_code == 200:

                data = response.json()

                results = data.get(
                    "results",
                    []
                )

                st.metric(
                    "Total Records",
                    data.get(
                        "total_records",
                        len(results)
                    )
                )

                if results:

                    st.dataframe(
                        results,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No site risk records available."
                    )

            else:

                st.error(
                    f"FastAPI returned HTTP "
                    f"{response.status_code}"
                )

        except requests.exceptions.RequestException as error:

            st.error(
                "Could not connect to the Site Risk API."
            )

            st.code(
                str(error)
            )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "Construction Risk Intelligence Platform | "
    "Agentic AI Safety Monitoring"
)