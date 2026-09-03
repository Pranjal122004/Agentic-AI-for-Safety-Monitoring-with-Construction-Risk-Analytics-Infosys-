import streamlit as st
import pandas as pd
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.agents.site_risk_agent import SiteRiskAgent


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Construction Risk Intelligence",
    page_icon="🏗️",
    layout="wide"
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🏗️ Construction Risk Intelligence Platform")
st.subheader("Agentic AI - Site Risk Monitoring Dashboard")

st.markdown(
    "This dashboard monitors construction site conditions, "
    "detects hazards and calculates site risk scores."
)


# --------------------------------------------------
# Load Data
# --------------------------------------------------

@st.cache_data
def load_risk_data():

    agent = SiteRiskAgent()

    data_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend",
        "data",
        "site_monitoring.csv"
    )

    results = agent.analyze_dataset(data_file)

    return pd.DataFrame(results)


df = load_risk_data()


# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------

st.sidebar.header("🔎 Filters")

sites = ["All"] + sorted(df["site_id"].unique().tolist())

selected_site = st.sidebar.selectbox(
    "Select Site",
    sites
)

risk_levels = [
    "All",
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
]

selected_risk = st.sidebar.selectbox(
    "Select Risk Level",
    risk_levels
)


# Apply site filter

filtered_df = df.copy()

if selected_site != "All":
    filtered_df = filtered_df[
        filtered_df["site_id"] == selected_site
    ]


# Apply risk filter

if selected_risk != "All":
    filtered_df = filtered_df[
        filtered_df["risk_level"] == selected_risk
    ]


# --------------------------------------------------
# Dashboard Metrics
# --------------------------------------------------

st.header("📊 Risk Overview")

total_records = len(filtered_df)

high_risk = len(
    filtered_df[
        filtered_df["risk_level"] == "HIGH"
    ]
)

critical_risk = len(
    filtered_df[
        filtered_df["risk_level"] == "CRITICAL"
    ]
)

average_score = (
    round(filtered_df["risk_score"].mean(), 2)
    if len(filtered_df) > 0
    else 0
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monitoring Records",
    total_records
)

col2.metric(
    "High Risk",
    high_risk
)

col3.metric(
    "Critical Risk",
    critical_risk
)

col4.metric(
    "Average Risk Score",
    average_score
)


# --------------------------------------------------
# Risk Score Chart
# --------------------------------------------------

st.header("📈 Risk Score by Site and Time")

if not filtered_df.empty:

    chart_df = filtered_df.copy()

    chart_df["label"] = (
        chart_df["site_id"]
        + " - "
        + chart_df["timestamp"].astype(str)
    )

    chart_df = chart_df.set_index("label")

    st.bar_chart(
        chart_df["risk_score"]
    )

else:

    st.warning("No records match the selected filters.")


# --------------------------------------------------
# Risk Level Distribution
# --------------------------------------------------

st.header("🚦 Risk Level Distribution")

if not filtered_df.empty:

    risk_distribution = (
        filtered_df["risk_level"]
        .value_counts()
        .reindex(
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            fill_value=0
        )
    )

    st.bar_chart(risk_distribution)


# --------------------------------------------------
# Site-wise Risk
# --------------------------------------------------

st.header("🏗️ Site-wise Risk Summary")

if not filtered_df.empty:

    site_summary = (
        filtered_df
        .groupby("site_id")
        .agg(
            Average_Risk=("risk_score", "mean"),
            Maximum_Risk=("risk_score", "max"),
            Records=("risk_score", "count")
        )
        .round(2)
    )

    st.dataframe(
        site_summary,
        use_container_width=True
    )


# --------------------------------------------------
# Hazard Summary
# --------------------------------------------------

st.header("⚠️ Detected Hazards")

hazard_counts = {}

for hazards in filtered_df["hazards"]:

    for hazard in hazards:

        if hazard not in hazard_counts:
            hazard_counts[hazard] = 0

        hazard_counts[hazard] += 1


if hazard_counts:

    hazard_df = pd.DataFrame(
        list(hazard_counts.items()),
        columns=["Hazard", "Occurrences"]
    )

    hazard_df = hazard_df.sort_values(
        "Occurrences",
        ascending=False
    )

    st.bar_chart(
        hazard_df.set_index("Hazard")
    )

else:

    st.success("No hazards detected.")


# --------------------------------------------------
# Detailed Monitoring Data
# --------------------------------------------------

st.header("📋 Detailed Risk Monitoring")

display_df = filtered_df[
    [
        "site_id",
        "timestamp",
        "risk_score",
        "risk_level",
        "hazards",
        "recommendation"
    ]
].copy()

st.dataframe(
    display_df,
    use_container_width=True
)


# --------------------------------------------------
# Critical Risk Alerts
# --------------------------------------------------

st.header("🚨 Critical Risk Alerts")

critical_df = filtered_df[
    filtered_df["risk_level"] == "CRITICAL"
]

if not critical_df.empty:

    for _, row in critical_df.iterrows():

        st.error(
            f"🚨 {row['site_id']} | "
            f"{row['timestamp']} | "
            f"Risk Score: {row['risk_score']} | "
            f"Hazards: {', '.join(row['hazards'])}"
        )

else:

    st.success("No critical risks detected.")


# --------------------------------------------------
# Recommendations
# --------------------------------------------------

st.header("💡 Safety Recommendations")

if not filtered_df.empty:

    for _, row in filtered_df.iterrows():

        st.info(
            f"**{row['site_id']} — {row['risk_level']} Risk "
            f"({row['risk_score']})**: "
            f"{row['recommendation']}"
        )