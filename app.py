import streamlit as st
import pandas as pd
import requests
import time

API_DATA_URL = "https://wastewater-api-ymfn.onrender.com/api/download_data"

st.set_page_config(page_title="Wastewater Telemetry", layout="wide")
st.title("Wastewater Monitoring Dashboard")

def fetch_telemetry():
    try:
        response = requests.get(API_DATA_URL, timeout=10)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

df = fetch_telemetry()

if not df.empty:
    df['pH_Level'] = pd.to_numeric(df['pH_Level'])
    df['Turbidity_NTU'] = pd.to_numeric(df['Turbidity_NTU'])
    
    latest_reading = df.iloc[-1]
    latest_ph = latest_reading['pH_Level']
    latest_location = latest_reading['Location']
    
    if latest_ph > 9.0 or latest_ph < 6.0:
        st.error(f"🚨 CRITICAL HAZARD DETECTED at {latest_location} | pH Level: {latest_ph}")
        st.toast(f"Red Alert at {latest_location}", icon="🚨")
    else:
        st.success("🟢 All systems operating within normal parameters.")

    st.dataframe(df)
else:
    st.info("Awaiting telemetry from sensor network...")

time.sleep(5)
st.rerun()