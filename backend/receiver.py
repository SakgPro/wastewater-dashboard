from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import csv
from datetime import datetime
import json
import os
import time
import requests

app = FastAPI()

class SensorPayload(BaseModel):
    node_id: str
    location: str
    ph_level: float
    turbidity_ntu: float

cooldown_tracker = {}

def send_alert_email_http(location, ph_level, target_email):
    api_key = os.environ.get("EMAIL_API_KEY")
    sender_email = os.environ.get("SENDER_EMAIL", "sakshamg389@gmail.com")
    
    print(f"DEBUG: Preparing email. Sender: {sender_email}, Target: {target_email}")
    
    if not api_key:
        print("DEBUG ERROR: EMAIL_API_KEY is missing from environment variables!")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"email": sender_email},
        "to": [{"email": target_email}],
        "subject": f"URGENT: Red Alert at {location}",
        "textContent": f"CRITICAL HAZARD DETECTED\n\nLocation: {location}\npH Level: {ph_level}\n\nImmediate maintenance crew dispatch required."
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"DEBUG BREVO STATUS CODE: {response.status_code}")
        print(f"DEBUG BREVO RESPONSE: {response.text}")
    except Exception as e:
        print(f"DEBUG REQUEST FAILED: {e}")

@app.post("/api/sensor_data")
def receive_data(payload: SensorPayload, background_tasks: BackgroundTasks):
    file_exists = os.path.isfile("synthetic_wastewater_data.csv")
    
    with open("synthetic_wastewater_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Location", "pH_Level", "Viral_Load_cp_ml", "Turbidity_NTU", "Antibiotics_ng_L"])
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, payload.location, payload.ph_level, 0.0, payload.turbidity_ntu, 0.0])

    if payload.ph_level > 9.0 or payload.ph_level < 6.0:
        config_file = "alert_config.json"
        notifications_enabled = True
        target = "sakshamg389@gmail.com"

        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as config_in:
                    config = json.load(config_in)
                    notifications_enabled = config.get("notifications_enabled", True)
                    target = config.get("target_email", "sakshamg389@gmail.com")
            except Exception:
                pass
                
        if notifications_enabled:
            current_time = time.time()
            last_alert = cooldown_tracker.get(payload.location, 0)
            
            if current_time - last_alert > 300:
                background_tasks.add_task(send_alert_email_http, payload.location, payload.ph_level, target)
                cooldown_tracker[payload.location] = current_time

    return {"status": "success", "recorded_ph": payload.ph_level}

@app.get("/healthz")
def health_check():
    return {"status": "healthy"}

@app.get("/api/download_data")
def download_data():
    file_path = "synthetic_wastewater_data.csv"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return data
    return []