import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from alerts import apply_thresholds

st.set_page_config(page_title="Campus Health Alert Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("synthetic_wastewater_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df = apply_thresholds(df)
    return df

df = load_data()

st.title("🦠 Campus Wastewater Health Alert Dashboard")
st.markdown("Proactive environmental monitoring for early disease detection and sanitary management.")

st.sidebar.header("Filter Data")
locations = df['Location'].unique()
selected_loc = st.sidebar.selectbox("Select Location", ["All Campus"] + list(locations))

if selected_loc != "All Campus":
    filtered_df = df[df['Location'] == selected_loc]
else:
    filtered_df = df

latest_date = df['Date'].max()
latest_data = df[df['Date'] == latest_date]

tab1, tab2, tab3 = st.tabs(["📊 Live Dashboard", "⚠️ Response Protocols", "📑 Deployment & Ethics"])

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

    st.subheader("📍 Campus Node Monitoring Map")
    
    geo_nodes = {
        "Surajtal": {"lat": 31.7754, "lon": 76.9855},
        "Dashir": {"lat": 31.7759, "lon": 76.9850},
        "Gauri Kund": {"lat": 31.7761, "lon": 76.9845},
        "Suvalsar": {"lat": 31.7765, "lon": 76.9840},
        "Vyas Kund": {"lat": 31.7770, "lon": 76.9835},
        "Cedar Mess": {"lat": 31.7745, "lon": 76.9860},
        "Maple Mess": {"lat": 31.7748, "lon": 76.9865},
        "North Academic Block": {"lat": 31.7735, "lon": 76.9840},
        "South Academic Block": {"lat": 31.7725, "lon": 76.9830}
    }
    
    m = folium.Map(location=[31.7754, 76.9855], zoom_start=16, tiles="OpenStreetMap")
    
    for node_name, coords in geo_nodes.items():
        node_latest = latest_data[latest_data['Location'] == node_name]
        
        if not node_latest.empty:
            status = node_latest['Status'].values[0]
            viral = node_latest['Viral_Load_cp_ml'].values[0]
            ph = node_latest['pH_Level'].values[0]
            details = node_latest['Alert_Details'].values[0]
            
            color_map = {"Green": "green", "Yellow": "orange", "Red": "red"}
            marker_color = color_map.get(status, "blue")
            
            popup_html = f"""
            <strong>{node_name}</strong><br>
            Status: {status}<br>
            Viral Load: {viral} cp/ml<br>
            pH Level: {ph}<br>
            Details: {details}
            """
            
            folium.Marker(
                location=[coords["lat"], coords["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{node_name} - {status}",
                icon=folium.Icon(color=marker_color, icon="info-sign")
            ).add_to(m)

    st_folium(m, width=1400, height=450)

    st.divider()
    
    st.subheader("Biomarker Trends (30 Days)")
    fig_viral = px.line(filtered_df, x='Date', y='Viral_Load_cp_ml', color='Location', title="Viral Load Over Time")
    fig_ph = px.line(filtered_df, x='Date', y='pH_Level', color='Location', title="pH Level Over Time")
    
    fig_viral.add_hline(y=400, line_dash="dash", line_color="red")
    fig_ph.add_hrect(y0=6.5, y1=8.5, line_width=0, fillcolor="green", opacity=0.1)
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(fig_viral, use_container_width=True)
    with col_chart2:
        st.plotly_chart(fig_ph, use_container_width=True)
        
    st.subheader("Recent Alert Logs")
    alert_data = filtered_df[filtered_df['Status'] != 'Green'].sort_values(by='Date', ascending=False)
    st.dataframe(alert_data[['Date', 'Location', 'Status', 'Alert_Details', 'Viral_Load_cp_ml', 'pH_Level']], use_container_width=True)

with tab2:
    st.header("Suggested Actions After Warning Signals")
    st.markdown("Automated response plans based on active threshold breaches.")
    
    active_reds = latest_data[latest_data['Status'] == 'Red']
    if not active_reds.empty:
        for _, row in active_reds.iterrows():
            st.error(f"🚨 **CRITICAL ALERT at {row['Location']}**")
            st.markdown(f"**Trigger:** {row['Alert_Details']}")
            if "Viral" in row['Alert_Details']:
                st.markdown("- **Action 1:** Dispatch medical personnel for randomized clinical screening in this building.")
                st.markdown("- **Action 2:** Increase sanitization frequency of common areas and washrooms.")
                st.markdown("- **Action 3:** Issue precautionary advisory to residents to report flu-like symptoms.")
            if "pH" in row['Alert_Details'] or "Chemical" in row['Alert_Details']:
                st.markdown("- **Action 1:** Dispatch plumbing crew to inspect for illegal chemical dumping or pipe corrosion.")
                st.markdown("- **Action 2:** Temporarily halt greywater recycling from this node.")
    else:
        st.success("✅ No critical alerts active. Standard operational protocols apply.")

with tab3:
    st.header("Campus Deployment Plan")
    st.markdown("""
    **Phase 1: Node Identification (Weeks 1-2)**
    - Map key effluent convergence points outside high-density hostels and academic blocks.
    
    **Phase 2: Hardware Installation (Weeks 3-4)**
    - Install autosamplers and IoT multi-parameter sondes at mapped nodes.
    
    **Phase 3: Sampling Routine & Dashboard Integration (Weeks 5-8)**
    - Establish a twice-weekly physical sampling schedule for PCR viral load testing.
    - Connect IoT sensor telemetry directly via API to this Streamlit monitoring dashboard.
    """)
    
    st.divider()
    
    st.header("Privacy and Ethics Concerns")
    st.warning("**Data Anonymization Protocol Active**")
    st.markdown("""
    - **Building-Level Aggregation:** Sensors are placed at the main building outflow. We do not track individual floors or wings, making it mathematically impossible to trace an infection back to a specific student.
    - **Targeted Biomarkers Only:** Laboratory analysis is restricted exclusively to agreed-upon public health markers.
    - **Transparent Communication:** The student body is fully informed regarding what data is being collected and how it is used to safeguard campus health.
    """)