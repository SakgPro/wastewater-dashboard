import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import json
import os

st.set_page_config(page_title="Campus Health Alert Dashboard", layout="wide")

def get_alert_status(ph, viral_load, turbidity, antibiotics, location):
    alerts = []
    suggested_action = "Maintain standard operational sampling."
    status = "Green"
    
    if pd.isna(ph):
        ph = 7.0
    if pd.isna(viral_load):
        viral_load = 0.0
    if pd.isna(turbidity):
        turbidity = 0.0
    if pd.isna(antibiotics):
        antibiotics = 0.0
        
    if ph < 6.0 or ph > 9.0:
        alerts.append("Red (Critical pH Hazard)")
        suggested_action = "Dispatch maintenance to inspect for industrial/lab chemical dumping."
    elif ph < 6.5 or ph > 8.5:
        alerts.append("Yellow (pH Warning)")
        suggested_action = "Monitor node for continued acidity/alkalinity shifts."

    if viral_load > 400:
        alerts.append("Red (Active Viral Outbreak)")
        suggested_action = "Alert campus clinic. Deploy randomized clinical screening in this building."
    elif viral_load > 180:
        alerts.append("Yellow (Elevated Viral Shedding)")
        suggested_action = "Increase sanitization of common washrooms and mess halls."

    if antibiotics > 120:
        alerts.append("Yellow (High Antibiotic Load)")
        if "Active Viral Outbreak" not in "".join(alerts):
            suggested_action = "Investigate potential bacterial outbreak in this building."

    limit = 18.0 if type(location) == str and "Mess" in location else 12.0
    if turbidity > limit:
        alerts.append("Red (Sewer/Organic Congestion)")
        suggested_action = "Clear grease traps and inspect primary outflow pipes."

    if any("Red" in alert for alert in alerts):
        status = "Red"
    elif any("Yellow" in alert for alert in alerts):
        status = "Yellow"
        
    if status == "Green":
        alerts = ["Normal Baseline"]

    return status, alerts, suggested_action

def apply_thresholds(df):
    status_list = []
    details_list = []
    actions_list = []
    
    for _, row in df.iterrows():
        status, details, action = get_alert_status(
            row['pH_Level'], 
            row['Viral_Load_cp_ml'], 
            row['Turbidity_NTU'], 
            row['Antibiotics_ng_L'],
            row['Location']
        )
        status_list.append(status)
        details_list.append(", ".join(details))
        actions_list.append(action)
        
    df['Status'] = status_list
    df['Alert_Details'] = details_list
    df['Suggested_Action'] = actions_list
    return df

def load_data():
    df = pd.read_csv("synthetic_wastewater_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['pH_Level'] = pd.to_numeric(df['pH_Level'], errors='coerce')
    df['Viral_Load_cp_ml'] = pd.to_numeric(df['Viral_Load_cp_ml'], errors='coerce')
    df['Turbidity_NTU'] = pd.to_numeric(df['Turbidity_NTU'], errors='coerce')
    df['Antibiotics_ng_L'] = pd.to_numeric(df['Antibiotics_ng_L'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = apply_thresholds(df)
    return df

df = load_data()

st.sidebar.title("Controls")
if st.sidebar.button("Force Sync Data"):
    st.rerun()

st.sidebar.header("Filter Data")
locations = df['Location'].dropna().unique()
selected_loc = st.sidebar.selectbox("Select Location", ["All Campus"] + list(locations))
time_range = st.sidebar.radio("Select Time Range", ["7 Days", "30 Days", "All Time"], index=1)

st.sidebar.divider()
st.sidebar.header("Alert Configurations")

config_file = "alert_config.json"
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    config = {"notifications_enabled": False, "target_email": "sakshamg389@gmail.com"}

notifications_enabled = st.sidebar.checkbox("Enable Email Notifications", value=config.get("notifications_enabled", False))
target_email = st.sidebar.text_input("Alert Receiving Email", value=config.get("target_email", "sakshamg389@gmail.com"))

if notifications_enabled != config.get("notifications_enabled") or target_email != config.get("target_email"):
    with open(config_file, "w") as f:
        json.dump({"notifications_enabled": notifications_enabled, "target_email": target_email}, f)

if selected_loc != "All Campus":
    filtered_df = df[df['Location'] == selected_loc]
else:
    filtered_df = df

max_date = df['Date'].max()
if time_range == "7 Days":
    cutoff_date = max_date - pd.Timedelta(days=7)
    filtered_df = filtered_df[filtered_df['Date'] >= cutoff_date]
elif time_range == "30 Days":
    cutoff_date = max_date - pd.Timedelta(days=30)
    filtered_df = filtered_df[filtered_df['Date'] >= cutoff_date]

latest_data = df.sort_values('Date').groupby('Location').tail(1)

st.title("🦠 Campus Wastewater Health Alert Dashboard")
st.markdown("Proactive environmental monitoring for early disease detection and sanitary management.")

tab1, tab2 = st.tabs(["📊 Live Dashboard", "📑 Deployment & Ethics"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg pH Level", f"{latest_data['pH_Level'].mean():.2f}")
    with col2:
        st.metric("Avg Viral Load (cp/ml)", f"{latest_data['Viral_Load_cp_ml'].mean():.2f}")
    with col3:
        active_alerts = len(latest_data[latest_data['Status'] == 'Red'])
        st.metric("Active Critical Alerts", active_alerts)
    
    st.divider()

    active_reds = latest_data[latest_data['Status'] == 'Red']
    if not active_reds.empty:
        st.error(f"🚨 {len(active_reds)} Critical Alert(s) Detected! Immediate action required.")
        for _, row in active_reds.iterrows():
            with st.expander(f"View Action Plan: {row['Location']} - {row['Alert_Details']}", expanded=True):
                st.write(f"**Suggested Action:** {row['Suggested_Action']}")
                if "Viral" in row['Alert_Details']:
                    st.write("- Action 1: Dispatch medical personnel for randomized clinical screening in this building.")
                    st.write("- Action 2: Increase sanitization frequency of common areas and washrooms.")
                    st.write("- Action 3: Issue precautionary advisory to residents to report flu-like symptoms.")
                if "pH" in row['Alert_Details'] or "Chemical" in row['Alert_Details']:
                    st.write("- Action 1: Dispatch plumbing crew to inspect for illegal chemical dumping or pipe corrosion.")
                    st.write("- Action 2: Temporarily halt greywater recycling from this node.")
        st.divider()

    st.subheader("📍 Campus Node Monitoring Map")
    
    geo_nodes = {
        "Surajtal": {"lat": 31.7816, "lon": 76.9966},
        "Dashir": {"lat": 31.7818, "lon": 76.9968},
        "Gauri Kund": {"lat": 31.7718, "lon": 76.9838},
        "Suvalsar": {"lat": 31.7720, "lon": 76.9840},
        "Vyas Kund": {"lat": 31.7722, "lon": 76.9842},
        "Cedar Mess": {"lat": 31.7715, "lon": 76.9845},
        "Maple Mess": {"lat": 31.7810, "lon": 76.9960},
        "North Academic Block": {"lat": 31.7814, "lon": 76.9964},
        "South Academic Block": {"lat": 31.7716, "lon": 76.9836}
    }
        
    m = folium.Map(location=[31.7765, 76.9900], zoom_start=15, tiles="OpenStreetMap")
    
    for node_name, coords in geo_nodes.items():
        node_latest = latest_data[latest_data['Location'] == node_name]
        
        if not node_latest.empty:
            status = node_latest['Status'].values[0]
            viral = node_latest['Viral_Load_cp_ml'].values[0]
            ph = node_latest['pH_Level'].values[0]
            details = node_latest['Alert_Details'].values[0]
            
            color_map = {"Green": "green", "Yellow": "orange", "Red": "red"}
            marker_color = color_map.get(status, "blue")
            
            popup_html = f"<strong>{node_name}</strong><br>Status: {status}<br>Viral Load: {viral} cp/ml<br>pH Level: {ph}<br>Details: {details}"
            
            folium.Marker(
                location=[coords["lat"], coords["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{node_name} - {status}",
                icon=folium.Icon(color=marker_color, icon="info-sign")
            ).add_to(m)

    st_folium(m, width=1400, height=450)

    st.divider()
    
    st.subheader(f"Biomarker Trends ({time_range})")
    fig_viral = px.line(filtered_df, x='Date', y='Viral_Load_cp_ml', color='Location', title="Viral Load Over Time")
    fig_ph = px.line(filtered_df, x='Date', y='pH_Level', color='Location', title="pH Level Over Time")
    
    fig_viral.add_hline(y=400, line_dash="dash", line_color="red")
    fig_ph.add_hrect(y0=6.5, y1=8.5, line_width=0, fillcolor="green", opacity=0.1)
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(fig_viral, use_container_width=True)
    with col_chart2:
        st.plotly_chart(fig_ph, use_container_width=True)
        
    st.subheader(f"Alert Logs ({time_range})")
    alert_data = filtered_df[filtered_df['Status'] != 'Green'].sort_values(by='Date', ascending=False)
    st.dataframe(alert_data[['Date', 'Location', 'Status', 'Alert_Details', 'Viral_Load_cp_ml', 'pH_Level']], use_container_width=True)

with tab2:
    st.header("Campus Deployment Plan")
    st.markdown("**Phase 1: Node Identification (Weeks 1-2)**\n- Map key effluent convergence points outside high-density hostels and academic blocks.\n\n**Phase 2: Hardware Installation (Weeks 3-4)**\n- Install autosamplers and IoT multi-parameter sondes at mapped nodes.\n\n**Phase 3: Sampling Routine & Dashboard Integration (Weeks 5-8)**\n- Establish a twice-weekly physical sampling schedule for PCR viral load testing.\n- Connect IoT sensor telemetry directly via API to this Streamlit monitoring dashboard.")