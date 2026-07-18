import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_iit_mandi_data(days=30):
    campus_nodes = [
        "Mani Mahesh Hostel", "Nako Hostel", "Renuka Hostel", "Chandrataal Hostel", "Parashar Hostel",
        "Gauri Kund Hostel", "Dashir Hostel", "Suvalsar Hostel", "Surajtal Hostel", "Vyas Kund Hostel",
        "Cedar Mess", "Maple Mess", "Gulmohar Mess", 
        "Pine Mess", "Oak Mess", "Alder Mess",
        "North Campus Academic Block", "South Campus Academic Block", "A-9 Building",
        "Sports Complex", "C.V. Raman Guest House", "Uhl Guest House", 
        "North Health Centre", "South Health Centre", "Auditorium Complex"
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    for date in date_range:
        for node in campus_nodes:
            base_ph = np.random.normal(7.2, 0.3)
            
            if "Academic" in node and (date.day >= 12 and date.day <= 14):
                base_ph = np.random.normal(5.1, 0.2)
                
            ph = max(min(base_ph, 14.0), 0.0)
            
            if "Mess" in node:
                turbidity = max(np.random.normal(12.0, 2.0), 0.0)
            else:
                turbidity = max(np.random.normal(6.5, 1.2), 0.0)
            
            base_viral = max(np.random.normal(85.0, 15.0), 0.0)
            
            if node == "Dashir Hostel" and date > (end_date - timedelta(days=7)):
                days_active = (date - (end_date - timedelta(days=7))).days
                outbreak_spike = np.exp(days_active * 0.4) * 45.0
                viral_load = base_viral + outbreak_spike + np.random.normal(0, 25.0)
            elif node == "Mani Mahesh Hostel" and date > (end_date - timedelta(days=10)):
                days_active = (date - (end_date - timedelta(days=10))).days
                outbreak_spike = np.exp(days_active * 0.3) * 35.0
                viral_load = base_viral + outbreak_spike + np.random.normal(0, 20.0)
            else:
                viral_load = base_viral
                
            data.append({
                "Date": date.strftime('%Y-%m-%d'),
                "Location": node,
                "pH_Level": round(ph, 2),
                "Viral_Load_cp_ml": round(viral_load, 2),
                "Turbidity_NTU": round(turbidity, 2)
            })
            
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_iit_mandi_data(days=30)
    output_filename = "synthetic_wastewater_data.csv"
    df.to_csv(output_filename, index=False)