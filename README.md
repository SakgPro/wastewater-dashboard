# 🦠 My Campus Wastewater Health Alert System

Hey there! Welcome to my project. I built this real-time, cloud-based Internet of Things (IoT) ecosystem to handle proactive environmental monitoring and early disease detection across different campus nodes (like Surajtal, Dashir, Cedar Mess, and the Academic Blocks).

Basically, this system continuously tracks effluent data—things like pH levels, turbidity, and viral load. If the sensors pick up on a hazardous chemical dump or a potential viral outbreak, the system catches it and automatically triggers an alert so action can be taken immediately.

---

## 🔗 See It in Action

Want to see it working right now? You do not need to download anything; I have already deployed it to the cloud. Check out these links:

* **Live Dashboard:** [https://wastewater-dashboard-7kpwrsrsfrqeacdejgu8xn.streamlit.app/](https://wastewater-dashboard-7kpwrsrsfrqeacdejgu8xn.streamlit.app/)
* **Backend API Endpoint:** [https://wastewater-api-ymfn.onrender.com/api/download_data](https://wastewater-api-ymfn.onrender.com/api/download_data)

### How to Use These Links:

* **The Live Dashboard:** Just click the link to open the web app in your browser. You will immediately see the real-time map, active alerts, and trend charts I set up. It updates on its own!
* **The Backend API Endpoint:** If you click this link, you will see the raw JSON data of all the recorded sensor readings. If you are a developer, you can actually use this URL in your own scripts (using Python's `requests` library), `curl` commands, or Postman to programmatically grab my database.

---

## 📂 Under the Hood: How I Structured the Files

If you are looking through my repository, here is a quick breakdown of what each file actually does:

### Frontend & Analytics

* **`app.py`**
This is my main Streamlit application. I wrote this to continuously fetch live telemetry from my Render API, calculate hazard thresholds, and render the interactive Folium map and Plotly biomarker trend charts.
* **`alert_config.json`**
This just stores the configuration settings for the dashboard, keeping track of whether email notifications are turned on and where to send them.

### Backend & Cloud API

* **`receiver.py`**
This is the FastAPI backend server I deployed on Render. It sits there waiting to receive POST requests from the sensor network. Once it gets data, it saves it to the CSV database and uses a background task to trigger HTTP email alerts (via Brevo) if any critical thresholds are breached.
* **`synthetic_wastewater_data.csv`**
This is the persistent database file hosted on the Render server. It logs all the historical telemetry data with timestamps so the frontend has data to chart out trends.

### Edge / Sensor Level

* **`virtual_sensor.py`**
Since I am not using physical hardware right now, this Python script acts as my physical IoT hardware. It generates synthetic wastewater data and transmits the payload directly to the cloud backend over the internet.

### Configuration

* **`requirements.txt`**
This is just the list of all the Python dependencies (FastAPI, Streamlit, Pandas, Requests, Folium, etc.) needed to build and deploy the project.

---

## 🚀 Want to run it yourself?

If you clone this repository and want to play around with it on your own machine, here is what you need to do:

### 1. Feed data to the live system

To generate data from your own machine and send it to my live cloud backend, just run the sensor script in your terminal:

```bash
python virtual_sensor.py

```

### 2. Test the dashboard locally

If you want to edit the UI or test the frontend on your local machine before pushing changes, install the requirements and launch the Streamlit app:

```bash
pip install -r requirements.txt
streamlit run app.py

```
