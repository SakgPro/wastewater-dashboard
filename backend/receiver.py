import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class SensorPayload(BaseModel):
    node_id: str
    location: str
    ph_level: float
    turbidity_ntu: float

@app.post("/api/sensor_data")
async def receive_sensor_data(payload: SensorPayload):
    file_path = os.path.join(os.getcwd(), "synthetic_wastewater_data.csv")
    
    df = pd.read_csv(file_path)
    
    new_row = df[df['Location'] == payload.location].iloc[-1].copy()
    
    new_row['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row['pH_Level'] = payload.ph_level
    new_row['Turbidity_NTU'] = payload.turbidity_ntu
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(file_path, index=False)
    
    return {
        "status": "success", 
        "location": payload.location, 
        "file_written_to": file_path
    }