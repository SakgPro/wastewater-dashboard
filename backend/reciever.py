from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
import os

app = FastAPI()

class SensorPayload(BaseModel):
    node_id: str
    location: str
    ph_level: float
    turbidity_ntu: float

@app.post("/api/sensor_data")
async def receive_sensor_data(payload: SensorPayload):
    new_data = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Location": payload.location,
        "pH_Level": payload.ph_level,
        "Turbidity_NTU": payload.turbidity_ntu,
        "Viral_Load_cp_ml": 85.0,
        "Antibiotics_ng_L": 20.0
    }
    
    df = pd.DataFrame([new_data])
    file_path = "synthetic_wastewater_data.csv"
    
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)
        
    return {"status": "success", "recorded_location": payload.location}