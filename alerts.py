def get_alert_status(ph, viral_load, turbidity, antibiotics, location):
    alerts = []
    suggested_action = "Maintain standard operational sampling."
    status = "Green"
    
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

    limit = 18.0 if "Mess" in location else 12.0
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