from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage
import csv
from datetime import datetime
import json
import os
import time

app = FastAPI()

class SensorPayload(BaseModel):
    node_id: str
    location: str
    ph_level: float
    turbidity_ntu: float

cooldown_tracker = {}

def send_alert_email(location, ph_level, target_email):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    if not sender_email or not sender_password or not target_email:
        print("Alert Skipped: Missing environment variables or target email.")
        return

    try:
        msg = EmailMessage()
        msg.set_content(f"CRITICAL HAZARD DETECTED\n\nLocation: {location}\npH Level: {ph_level}\n\nImmediate maintenance crew dispatch required to inspect for chemical dumping.")
        msg['Subject'] = f"🚨 URGENT: Red Alert at {location}"
        msg['From'] = sender_email
        msg['To'] = target_email

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Alert email successfully dispatched to {target_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.post("/api/sensor_data")
async def receive_data(payload: SensorPayload):
    file_exists = os.path.isfile("synthetic_wastewater_data.csv")
    
    with open("synthetic_wastewater_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Location", "pH_Level", "Viral_Load_cp_ml", "Turbidity_NTU", "Antibiotics_ng_L"])
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, payload.location, payload.ph_level, 0.0, payload.turbidity_ntu, 0.0])

    if payload.ph_level > 9.0 or payload.ph_level < 6.0:
        config_file = "alert_config.json"
        if os.path.exists(config_file):
            with open(config_file, "r") as config_in:
                config = json.load(config_in)
                
            if config.get("notifications_enabled"):
                target = config.get("target_email")
                current_time = time.time()
                last_alert = cooldown_tracker.get(payload.location, 0)
                
                if current_time - last_alert > 300:
                    send_alert_email(payload.location, payload.ph_level, target)
                    cooldown_tracker[payload.location] = current_time

    return {"status": "success", "recorded_ph": payload.ph_level}

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}