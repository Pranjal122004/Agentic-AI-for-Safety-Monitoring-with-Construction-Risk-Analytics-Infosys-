import base64
import json
from io import BytesIO
import html

import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="SiteGuard AI | Construction Safety", page_icon="🦺", layout="wide", initial_sidebar_state="expanded")
API_BASE = "http://127.0.0.1:8000"
ANALYZE_URL = f"{API_BASE}/analyze-risk"
HEALTH_URL = f"{API_BASE}/health"
SITE_RISK_URL = f"{API_BASE}/site-risk"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#0b1020;--panel:#121a2d;--line:#293955;--text:#edf3ff;--muted:#9aabc7;--cyan:#53d8e8}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(ellipse at top left,#172746 0%,#0b1020 48%,#080d18 100%);color:var(--text)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#10192c,#0b1020);border-right:1px solid #25324a}
[data-testid="stSidebar"] *{color:#eaf1ff}
h1,h2,h3{color:#f4f7ff!important;letter-spacing:-.035em} p,label,li{color:#c6d2e8}
.eyebrow{color:#6ee7f2;font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.metric{background:linear-gradient(145deg,#17243b,#111a2c);border:1px solid #293955;border-radius:17px;padding:17px 18px;min-height:112px;transition:transform .18s,border-color .18s}
.metric:hover{transform:translateY(-3px);border-color:#53d8e8}
.metric-label{color:#9aabc7;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.metric-value{color:#f4f8ff;font-size:29px;font-weight:800;margin-top:8px;overflow-wrap:anywhere}
.metric-note{color:#93a7c7;font-size:12px;margin-top:3px}
.info-card{background:rgba(18,26,45,.88);border:1px solid #263650;border-radius:16px;padding:16px 18px;margin:8px 0}
.info-label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#9aabc7;font-weight:700}
.info-value{font-size:18px;font-weight:700;color:#edf3ff;margin-top:5px;overflow-wrap:anywhere}
div.stButton>button{border-radius:12px;min-height:44px;font-weight:700;border:1px solid #344762;background:linear-gradient(135deg,#1b2d48,#142238);color:#eff7ff;transition:all .18s}
div.stButton>button:hover{border-color:#53d8e8;color:#fff;transform:translateY(-1px)}
[data-testid="stFileUploader"]{background:#111b2e;border:1px dashed #3a5274;border-radius:16px;padding:14px}
[data-testid="stFileUploader"] *{color:#eaf1ff!important}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.block-container{animation:rise .35s ease-out both}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)


def safe_get(data, *keys, default=None):
    cur = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def metric_card(label, value, note=""):
    # Escape dynamic strings so backend text is shown as text, not interpreted as HTML.
    st.markdown(f'''<div class="metric"><div class="metric-label">{html.escape(str(label))}</div><div class="metric-value">{html.escape(str(value))}</div><div class="metric-note">{html.escape(str(note))}</div></div>''', unsafe_allow_html=True)


def info_card(label, value):
    if isinstance(value, (dict, list)):
        value = f"{len(value)} items" if isinstance(value, list) else f"{len(value)} fields"
    st.markdown(f'''<div class="info-card"><div class="info-label">{html.escape(str(label).replace('_',' ').title())}</div><div class="info-value">{html.escape(str(value))}</div></div>''', unsafe_allow_html=True)


def call_get(url, timeout=12):
    try:
        r = requests.get(url, timeout=timeout); r.raise_for_status(); return r.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def run_analysis(uploaded_file):
    payload = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
    try:
        r = requests.post(ANALYZE_URL, files=payload, timeout=180); r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get("error"): return None, str(data["error"])
        return data, None
    except requests.Timeout:
        return None, "Analysis timed out. Try a smaller image or check the backend terminal."
    except requests.RequestException as exc:
        return None, f"Could not reach backend: {exc}"


def detections_df(items):
    rows=[]
    for item in items if isinstance(items,list) else []:
        if isinstance(item,dict):
            conf=item.get("confidence")
            rows.append({"Detected item":item.get("class","Unknown"),"Confidence":conf,
                         "Confidence %":round(float(conf)*100,1) if isinstance(conf,(int,float)) else None,
                         "Review status":item.get("confidence_level","Not provided")})
    return pd.DataFrame(rows, columns=["Detected item","Confidence","Confidence %","Review status"])


def show_object_summary(title, obj):
    """Render structured agent dictionaries as human-readable cards, tables and charts—not raw JSON."""
    st.subheader(title)
    if not isinstance(obj,dict) or not obj:
        st.info("No details were returned for this section.")
        return
    scalar_items=[]; list_items=[]
    for k,v in obj.items():
        if isinstance(v,list): list_items.append((k,v))
        elif isinstance(v,dict):
            # Flatten one level of nested dictionaries into readable cards.
            for sk,sv in v.items(): scalar_items.append((f"{k} · {sk}",sv))
        else: scalar_items.append((k,v))
    if scalar_items:
        cols=st.columns(min(3,len(scalar_items)))
        for i,(k,v) in enumerate(scalar_items):
            with cols[i%len(cols)]: info_card(k,v)
    for key,values in list_items:
        st.markdown(f"**{key.replace('_',' ').title()}**")
        if not values:
            st.caption("None reported")
            continue
        if all(isinstance(x,dict) for x in values):
            df=pd.DataFrame(values)
            # Convert nested values to readable strings for a clean table.
            for col in df.columns:
                df[col]=df[col].apply(lambda x: ", ".join(f"{a}: {b}" for a,b in x.items()) if isinstance(x,dict) else ("; ".join(map(str,x)) if isinstance(x,list) else x))
            st.dataframe(df,use_container_width=True,hide_index=True)
            numeric=df.select_dtypes(include="number").columns.tolist()
            if numeric:
                metric=st.selectbox(f"Chart metric · {key}",numeric,key=f"chart_{title}_{key}")
                st.bar_chart(df[metric],use_container_width=True)
        elif all(isinstance(x,(str,int,float,bool)) or x is None for x in values):
            counts=pd.Series([str(x) for x in values]).value_counts()
            st.bar_chart(counts,use_container_width=True)
            st.dataframe(pd.DataFrame({"Item":values}),use_container_width=True,hide_index=True)
        else:
            st.dataframe(pd.DataFrame({"Details":[str(x) for x in values]}),use_container_width=True,hide_index=True)


def confidence_chart(df):
    if df.empty: return
    counts=df["Review status"].fillna("Not provided").value_counts()
    st.markdown("**Confidence distribution**")
    st.bar_chart(counts,use_container_width=True)

with st.sidebar:
    st.markdown("## 🦺 SiteGuard **AI**")
    st.caption("Construction Risk Intelligence")
    st.divider()
    page=st.radio("NAVIGATION",["Command Center","AI Vision Lab","Safety Review","Compliance","Site Risk","Insurance","Alerts & Reports"])
    st.divider()
    health,health_error=call_get(HEALTH_URL,4)
    st.markdown("**Backend status**")
    if health:
        st.success("API connected" if health.get("status")=="healthy" else "API responding")
        st.caption("PPE model: "+("Loaded" if health.get("ppe_model_loaded") else "Not loaded"))
    else:
        st.error("API unavailable")
        st.caption("Start FastAPI, then refresh this page.")
    st.divider(); st.caption("Local development • FastAPI + Streamlit")

if "risk_result" not in st.session_state: st.session_state.risk_result=None
if "last_upload_name" not in st.session_state: st.session_state.last_upload_name=None
result=st.session_state.risk_result
detections=safe_get(result,"detections",default=[]) if result else []
summary=safe_get(result,"reliability_summary",default={}) if result else {}
safety=safe_get(result,"safety_analysis",default={}) if result else {}
compliance=safe_get(result,"compliance_analysis",default={}) if result else {}
site=safe_get(result,"site_analysis",default={}) if result else {}
insurance=safe_get(result,"insurance_analysis",default={}) if result else {}
claim_risk=safe_get(insurance,"claim_risk",default={}) if insurance else {}

df_det=detections_df(detections)
st.markdown("<div class='eyebrow'>AI-POWERED CONSTRUCTION SAFETY</div>",unsafe_allow_html=True)
st.title(page)
st.caption("A unified workspace for PPE detection, safety review, site conditions, compliance signals, and insurance risk context.")
st.divider()

if page=="Command Center":
    a,b,c,d=st.columns(4)
    with a: metric_card("PPE detections",summary.get("total_detections","—"),"From latest image analysis")
    with b: metric_card("High confidence",summary.get("high_confidence_detections","—"),"Model confidence ≥ 80%")
    with c: metric_card("Needs review",summary.get("review_required_detections","—"),"Medium-confidence detections")
    with d:
        manual=summary.get("manual_review_required")
        metric_card("Manual review","Required" if manual else ("No" if manual is False else "—"),"Based on returned analysis")
    left,right=st.columns([1.15,.85],gap="large")
    with left:
        st.subheader("Start an inspection")
        st.write("Upload a construction-site image to run the full analysis.")
        upload=st.file_uploader("Choose a construction-site image",type=["jpg","jpeg","png","webp"],key="command_upload")
        if upload:
            st.image(upload,caption="Selected site image",use_container_width=True)
            if st.button("▶ Analyze site image",type="primary",use_container_width=True):
                with st.spinner("Checking PPE, safety, compliance, site and insurance context…"):
                    new_result,error=run_analysis(upload)
                if error: st.error(error)
                else:
                    st.session_state.risk_result=new_result; st.session_state.last_upload_name=upload.name
                    st.success("Inspection complete. Use the navigation to explore the visual results."); st.rerun()
    with right:
        st.subheader("Latest inspection")
        if result:
            st.success("Analysis ready")
            info_card("Image",st.session_state.last_upload_name or result.get("filename","Uploaded image"))
            info_card("Analysis time",result.get("analysis_timestamp","Not provided"))
            info_card("Detected objects",summary.get("total_detections",len(detections)))
            info_card("Manual review", "Required" if summary.get("manual_review_required") else "Not flagged")
        else: st.info("No inspection has been run in this session yet.")
    if result and not df_det.empty:
        st.subheader("At-a-glance detection charts")
        x,y=st.columns(2)
        with x: st.bar_chart(df_det["Detected item"].value_counts(),use_container_width=True)
        with y: confidence_chart(df_det)

elif page=="AI Vision Lab":
    st.subheader("Image inspection")
    upload=st.file_uploader("Upload image",type=["jpg","jpeg","png","webp"],key="vision_upload")
    x,y=st.columns(2,gap="large")
    with x:
        if upload: st.image(upload,caption="Original image",use_container_width=True)
    with y:
        st.info("Run the analysis to view AI detections and annotated output.")
        if upload and st.button("Run AI vision analysis",type="primary",use_container_width=True):
            with st.spinner("Analyzing image…"):
                new_result,error=run_analysis(upload)
            if error: st.error(error)
            else:
                st.session_state.risk_result=new_result; st.session_state.last_upload_name=upload.name
                st.success("Vision analysis complete."); st.rerun()
    if result:
        st.divider(); st.subheader("AI annotated image")
        encoded=result.get("annotated_image_base64")
        if encoded:
            try: st.image(BytesIO(base64.b64decode(encoded)),caption="Detected PPE and objects",use_container_width=True)
            except (ValueError,TypeError): st.warning("Annotated preview could not be displayed.")
        else: st.info("Annotated image was not included in the API response.")
        st.subheader("Detected objects")
        if df_det.empty: st.info("No detections were returned.")
        else:
            p,q=st.columns(2)
            with p: st.bar_chart(df_det["Detected item"].value_counts(),use_container_width=True)
            with q: confidence_chart(df_det)
            st.dataframe(df_det[["Detected item","Confidence %","Review status"]],use_container_width=True,hide_index=True)

elif page=="Safety Review":
    if not result: st.info("Run an image analysis from Command Center or AI Vision Lab first.")
    else:
        st.subheader("Safety overview")
        a,b,c=st.columns(3)
        with a: metric_card("Total detections",summary.get("total_detections",len(detections)))
        with b: metric_card("Low confidence",summary.get("low_confidence_detections",0),"Below 50% confidence")
        with c: metric_card("Manual review","Required" if summary.get("manual_review_required") else "Not flagged")
        if not df_det.empty:
            st.subheader("Detection confidence")
            filter_by=st.selectbox("Filter detections",["All","HIGH","REVIEW","LOW"])
            shown=df_det if filter_by=="All" else df_det[df_det["Review status"]==filter_by]
            a,b=st.columns(2)
            with a: st.bar_chart(shown["Detected item"].value_counts(),use_container_width=True)
            with b: confidence_chart(shown)
            st.dataframe(shown,use_container_width=True,hide_index=True)
        show_object_summary("Safety agent findings",safety)

elif page=="Compliance":
    if not result: st.info("Run an image analysis first.")
    else:
        total=safe_get(compliance,"total_reviews",default=0)
        violations=safe_get(compliance,"total_violations",default=0)
        status=safe_get(compliance,"compliance_status",default="Not provided")
        a,b,c=st.columns(3)
        with a: metric_card("Compliance status",status,"Returned by compliance agent")
        with b: metric_card("Violations",violations,"Reported in this analysis")
        with c: metric_card("Reviews",total,"Review items returned")
        if isinstance(compliance,dict):
            for list_key in ("violations","review_findings","recommendations"):
                vals=compliance.get(list_key,[])
                if vals:
                    st.subheader(list_key.replace("_"," ").title())
                    if all(isinstance(v,dict) for v in vals): st.dataframe(pd.DataFrame(vals),use_container_width=True,hide_index=True)
                    else: st.bar_chart(pd.Series([str(v) for v in vals]).value_counts(),use_container_width=True)
                    if not all(isinstance(v,dict) for v in vals): st.write(" ".join(f"• {v}" for v in vals))
            scalar={k:v for k,v in compliance.items() if not isinstance(v,(dict,list))}
            if scalar:
                st.subheader("Compliance indicators")
                cols=st.columns(min(3,len(scalar)))
                for i,(k,v) in enumerate(scalar.items()):
                    with cols[i%len(cols)]: info_card(k,v)
        st.download_button("⬇ Download compliance report",data=json.dumps(compliance,indent=2,ensure_ascii=False),file_name="compliance_analysis.json",mime="application/json")

elif page=="Site Risk":
    st.subheader("Site conditions dashboard")
    st.caption("These values come from the backend site-monitoring CSV, not from the uploaded image.")
    site_data,err=call_get(SITE_RISK_URL)
    if err: st.error(f"Could not load site data: {err}")
    else:
        rows=site_data.get("results",[]) if isinstance(site_data,dict) else []
        if rows:
            df_site=pd.DataFrame(rows)
            numeric=df_site.select_dtypes(include="number").columns.tolist()
            if numeric:
                cols=st.columns(min(4,len(numeric)))
                for i,col in enumerate(numeric[:4]):
                    val=df_site[col].iloc[-1] if not df_site[col].empty else "—"
                    with cols[i]: metric_card(col.replace("_"," ").title(),val,"Latest available record")
                metric=st.selectbox("Choose a site metric to chart",numeric)
                chart_df=df_site[[metric]].copy()
                if "timestamp" in df_site.columns: chart_df.index=df_site["timestamp"].astype(str)
                st.line_chart(chart_df,use_container_width=True)
            cat_cols=[c for c in df_site.columns if c not in numeric]
            if cat_cols:
                selected_cat=st.selectbox("Explore a site field",cat_cols)
                st.bar_chart(df_site[selected_cat].fillna("Not recorded").astype(str).value_counts(),use_container_width=True)
            with st.expander("View site records as a table"):
                st.dataframe(df_site,use_container_width=True,hide_index=True)
        else: st.info("The site-risk endpoint returned no records.")
        if result and isinstance(site,dict) and site:
            st.divider(); show_object_summary("Site context used in latest image analysis",site)

elif page=="Insurance":
    if not result: st.info("Run an image analysis first.")
    else:
        if isinstance(insurance,dict) and insurance:
            risk=insurance.get("risk_level",insurance.get("overall_risk","Not provided"))
            premium=insurance.get("premium_adjustment","Not provided")
            a,b=st.columns(2)
            with a: metric_card("Risk indicator",risk,"As returned by the agent")
            with b: metric_card("Premium adjustment",premium,"Only if supplied by backend")
            # Display structured insurance fields as cards and chart numeric values.
            show_object_summary("Insurance assessment",{k:v for k,v in insurance.items() if k!="claim_risk"})
        else: st.info("No insurance assessment details were returned.")
        if claim_risk: show_object_summary("Claim risk",claim_risk)

elif page=="Alerts & Reports":
    if not result: st.info("Run an image analysis first.")
    else:
        st.subheader("Inspection status")
        manual=summary.get("manual_review_required")
        if manual: st.warning("Manual review is flagged. A qualified person should verify the site findings.")
        else: st.success("The returned summary does not flag manual review.")
        a,b=st.columns(2)
        with a: info_card("Source image",result.get("filename",st.session_state.last_upload_name or "—"))
        with b: info_card("Analysis time",result.get("analysis_timestamp","—"))
        if not df_det.empty:
            st.subheader("Detection summary")
            st.bar_chart(df_det["Detected item"].value_counts(),use_container_width=True)
            confidence_chart(df_det)
        st.download_button("⬇ Download full inspection report",data=json.dumps(result,indent=2,ensure_ascii=False),file_name="construction_risk_analysis.json",mime="application/json",use_container_width=True)
        st.caption("The downloadable report preserves the complete backend response. It is not displayed as raw code on this page.")

st.divider()
st.caption("SiteGuard AI • Decision support only — verify findings on site.")
