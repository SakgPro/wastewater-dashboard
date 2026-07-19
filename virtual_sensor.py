import time
import random
import requests
from datetime import datetime

API_URL = "https://wastewater-api-ymfn.onrender.com/api/sensor_data"

CAMPUS_NODES = [
    "Surajtal",
    "Dashir",
    "Gauri Kund",
    "Suvalsar",
    "Vyas Kund",
    "Cedar Mess",
    "Maple Mess",
    "North Academic Block",
    "South Academic Block"
]

def simulate_node(location, is_anomaly):
    ph = round(random.uniform(7.0, 7.5), 2)
    turbidity = round(random.uniform(5.0, 8.0), 2)

    if is_anomaly:
        ph = round(random.uniform(10.0, 11.5), 2)
        turbidity = round(random.uniform(18.0, 25.0), 2)

    payload = {
        "node_id": f"{location.replace(' ', '_')}_Sim_01",
        "location": location,
        "ph_level": ph,
        "turbidity_ntu": turbidity
    }

    try:
        response = requests.post(API_URL, json=payload)
        time_str = datetime.now().strftime('%H:%M:%S')
        status = "🔴 ALERT" if is_anomaly else "🟢 NORMAL"
        print(f"[{time_str}] {status} | Transmitted {location} | pH: {ph} | Code: {response.status_code}")
    except Exception as e:
        print(f"API Connection Error: {e}")

if __name__ == "__main__":
    print("Virtual IoT Fleet Initialized.")
    print("Transmitting telemetry every 2 seconds...")
    
    cycle_count = 1
    
    while True:
        target_node = random.choice(CAMPUS_NODES)
        
        trigger_spike = (cycle_count % 7 == 0)
        
        simulate_node(target_node, trigger_spike)
        
        cycle_count += 1
        time.sleep(2)