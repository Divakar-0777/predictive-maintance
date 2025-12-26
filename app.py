import streamlit as st
from reportlab.pdfgen import canvas
import datetime

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Engine Condition Prediction", layout="wide")

# -------------------------------------------------
# SIDEBAR - FEATURE DESCRIPTIONS
# -------------------------------------------------
st.sidebar.title("Feature Descriptions")

st.sidebar.markdown("""
**Engine RPM**  
Speed of engine rotation. High RPM causes engine stress.

**Lub Oil Pressure**  
Ensures proper lubrication of engine parts.

**Fuel Pressure**  
Controls fuel delivery for combustion.

**Coolant Pressure**  
Maintains engine temperature stability.

**Lub Oil Temperature**  
High values degrade lubrication quality.

**Coolant Temperature**  
Indicates engine thermal condition.

**Temperature Difference**  
Shows uneven heat distribution.
""")

# -------------------------------------------------
# MAIN TITLE
# -------------------------------------------------
st.title("Engine Condition Prediction")

# -------------------------------------------------
# DATA SOURCE SELECTION
# -------------------------------------------------
use_sensor = st.checkbox("Use Live Sensor Data (ESP32 Simulation)")

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------
col1, col2 = st.columns(2)

try:
    from virtual_esp32 import get_sensor_data
    SENSOR_AVAILABLE = True
except ImportError:
    SENSOR_AVAILABLE = False
if use_sensor and SENSOR_AVAILABLE:
    try:
        sensor_data = get_sensor_data()
        st.success("Virtual ESP32 connected")

        rpm = sensor_data["engine_rpm"]
        oil_pressure = sensor_data["lub_oil_pressure"]
        fuel_pressure = sensor_data["fuel_pressure"]
        coolant_pressure = sensor_data["coolant_pressure"]
        oil_temp = sensor_data["lub_oil_temp"]
        coolant_temp = sensor_data["coolant_temp"]
        battery_voltage = sensor_data["battery_voltage"]

        with col1:
            st.metric("Engine RPM", rpm)
            st.metric("Lub Oil Pressure (bar)", oil_pressure)
            st.metric("Fuel Pressure (bar)", fuel_pressure)
            st.metric("Coolant Pressure (bar)", coolant_pressure)

        with col2:
            st.metric("Lub Oil Temperature (°C)", oil_temp)
            st.metric("Coolant Temperature (°C)", coolant_temp)
            st.metric("Battery Voltage (V)", battery_voltage)

    except Exception as e:
        st.error("Sensor error. Switching to manual input.")
        use_sensor = False

if not use_sensor:
    with col1:
        rpm = st.slider("Engine RPM", 600, 3000, 1100)
        oil_pressure = st.slider("Lub Oil Pressure (bar)", 0.0, 8.0, 3.6)
        fuel_pressure = st.slider("Fuel Pressure (bar)", 0.0, 25.0, 10.5)
        coolant_pressure = st.slider("Coolant Pressure (bar)", 0.0, 8.0, 3.7)

    with col2:
        oil_temp = st.slider("Lub Oil Temperature (°C)", 60, 120, 86)
        coolant_temp = st.slider("Coolant Temperature (°C)", 60, 130, 128)
        battery_voltage = st.slider("Battery Voltage (V)", 10.0, 13.0, 11.6)

# -------------------------------------------------
# DERIVED VALUE
# -------------------------------------------------
temp_diff = abs(oil_temp - coolant_temp)

# -------------------------------------------------
# BATTERY HEALTH
# -------------------------------------------------
st.subheader("Battery Health")

if battery_voltage >= 12.4:
    battery_status = "Healthy"
    batt_score = 90
elif battery_voltage >= 11.8:
    battery_status = "Warning"
    batt_score = 60
else:
    battery_status = "Critical – Switch-Shot Required"
    batt_score = 30

st.write(f"**Battery Status:** {battery_status}")

# -------------------------------------------------
# DIAGNOSTICS LOGIC
# -------------------------------------------------
def diagnose_issues(data):
    affected_parts = []
    advisories = []

    # Lubrication System
    if data['lub_oil_pressure'] < 2.5:
        affected_parts.append("Lubrication System (Low Pressure)")
        advisories.append("Check oil pump and oil level immediately.")
    if data['lub_oil_temp'] > 100:
        affected_parts.append("Lubrication System (Overheating)")
        advisories.append("Inspect oil cooler and check for blockages.")

    # Cooling System
    if data['coolant_temp'] > 110:
        affected_parts.append("Cooling System (Overheating)")
        advisories.append("Check coolant level, radiator, and thermostat.")
    if data['coolant_pressure'] < 1.0: # Assuming low pressure is bad
        affected_parts.append("Cooling System (Leak/Pressure Loss)")
        advisories.append("Inspect hoses and radiator cap for leaks.")

    # Fuel System
    if data['fuel_pressure'] < 6.0:
        affected_parts.append("Fuel System (Low Pressure)")
        advisories.append("Check fuel filter and fuel pump.")

    # Electrical System
    if data['battery_voltage'] < 11.8:
        affected_parts.append("Electrical System (Battery)")
        advisories.append("Test battery health and charging system.")

    # General Engine
    if data['temp_diff'] > 40:
        affected_parts.append("Engine Block (Uneven Heating)")
        advisories.append("Check for coolant flow restrictions or blocked passages.")

    if not affected_parts:
        affected_parts.append("None")
        advisories.append("System operating within normal parameters.")

    return affected_parts, advisories

import joblib
import pandas as pd

# Load Model
try:
    model = joblib.load("vehicle_health_model.pkl")
except Exception as e:
    st.error(f"Error loading model: {e}")
    model = None

# ... (existing code) ...

# -------------------------------------------------
# OVERALL VEHICLE HEALTH (ML PREDICTION)
# -------------------------------------------------
st.subheader("Overall Vehicle Health (ML Prediction)")

# Prepare input for model
input_data = pd.DataFrame([{
    "engine_rpm": rpm,
    "lub_oil_pressure": oil_pressure,
    "fuel_pressure": fuel_pressure,
    "coolant_pressure": coolant_pressure,
    "lub_oil_temp": oil_temp,
    "coolant_temp": coolant_temp,
    "battery_voltage": battery_voltage,
    "temp_diff": temp_diff
}])

if model:
    # Get probabilities
    probs = model.predict_proba(input_data)[0]
    classes = model.classes_
    
    # Create a dictionary for easier access
    prob_dict = {cls: round(prob * 100, 1) for cls, prob in zip(classes, probs)}
    
    # Determine dominant status
    vehicle_status = model.predict(input_data)[0]
    
    # Color coding
    if vehicle_status == "Healthy":
        color = "green"
    elif vehicle_status == "Warning":
        color = "orange"
    else:
        color = "red"

    # Display Probabilities
    st.markdown("### Health Probability Analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Healthy Probability", f"{prob_dict.get('Healthy', 0)}%")
    c2.metric("Warning Probability", f"{prob_dict.get('Warning', 0)}%")
    c3.metric("Critical Probability", f"{prob_dict.get('Critical', 0)}%")

    st.markdown(f"**Overall Status:** <span style='color:{color}; font-size:20px'>{vehicle_status}</span>", unsafe_allow_html=True)

else:
    st.warning("Model not loaded. Using fallback logic.")
    vehicle_status = "Unknown"
    prob_dict = {}

# -------------------------------------------------
# DIAGNOSTICS DISPLAY
# -------------------------------------------------
st.subheader("Diagnostics & Advisories")
affected_parts, advisories = diagnose_issues({
    "lub_oil_pressure": oil_pressure,
    "lub_oil_temp": oil_temp,
    "coolant_temp": coolant_temp,
    "coolant_pressure": coolant_pressure,
    "fuel_pressure": fuel_pressure,
    "battery_voltage": battery_voltage,
    "temp_diff": temp_diff
})

st.write("**Affected Systems:**")
for part in affected_parts:
    st.write(f"- {part}")

st.write("**Advisories:**")
for advice in advisories:
    st.info(advice)

# -------------------------------------------------
# PDF REPORT GENERATION
# -------------------------------------------------
# -------------------------------------------------
# PDF REPORT GENERATION
# -------------------------------------------------
def generate_pdf(affected_parts, advisories, prob_dict):
    file_name = "vehicle_health_report.pdf"
    c = canvas.Canvas(file_name, pagesize=(595, 842))  # A4 size

    # ---------- HEADER ----------
    c.setFillColorRGB(0.1, 0.2, 0.4)  # Dark blue
    c.rect(0, 800, 595, 42, fill=1)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(30, 812, "Vehicle Health Diagnostic Report")

    # ---------- DATE ----------
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawRightString(565, 785, f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}")

    y = 750

    # ---------- SECTION: ENGINE PARAMETERS ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Engine Parameters")
    y -= 15
    c.line(30, y, 565, y)
    y -= 20

    c.setFont("Helvetica", 11)
    engine_data = [
        ("Engine RPM", f"{rpm}"),
        ("Oil Pressure", f"{oil_pressure} bar"),
        ("Fuel Pressure", f"{fuel_pressure} bar"),
        ("Coolant Pressure", f"{coolant_pressure} bar"),
        ("Oil Temperature", f"{oil_temp} °C"),
        ("Coolant Temperature", f"{coolant_temp} °C"),
    ]

    for label, value in engine_data:
        c.drawString(40, y, label)
        c.drawRightString(560, y, value)
        y -= 18

    # ---------- SECTION: BATTERY HEALTH ----------
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Battery Health")
    y -= 15
    c.line(30, y, 565, y)
    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(40, y, "Battery Voltage")
    c.drawRightString(560, y, f"{battery_voltage} V")
    y -= 18

    c.drawString(40, y, "Battery Status")
    c.drawRightString(560, y, battery_status)
    y -= 25

    # ---------- SECTION: OVERALL VEHICLE HEALTH ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Overall Vehicle Health")
    y -= 15
    c.line(30, y, 565, y)
    y -= 25

    c.setFont("Helvetica", 12)
    c.drawString(40, y, "Health Score")
    c.drawRightString(560, y, f"{vehicle_score}%")
    y -= 20

    c.setFont("Helvetica", 12)
    c.drawString(40, y, "Vehicle Condition")
    c.drawRightString(560, y, vehicle_status)
    y -= 20
    
    if prob_dict:
        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Healthy: {prob_dict.get('Healthy', 0)}% | Warning: {prob_dict.get('Warning', 0)}% | Critical: {prob_dict.get('Critical', 0)}%")
    y -= 30

    # ---------- SECTION: DIAGNOSTICS ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Diagnostics & Affected Systems")
    y -= 15
    c.line(30, y, 565, y)
    y -= 20

    c.setFont("Helvetica", 11)
    for part in affected_parts:
        c.drawString(40, y, f"- {part}")
        y -= 15
    y -= 10

    # ---------- RECOMMENDATION ----------
    # ---------- RECOMMENDATION ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Advisories & Recommendations")
    y -= 15
    c.line(30, y, 565, y)
    y -= 20

    c.setFont("Helvetica", 11)
    for advice in advisories:
        c.drawString(40, y, f"- {advice}")
        y -= 15

    # ---------- FOOTER ----------
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        297,
        30,
        "This report is auto-generated using AI-based vehicle health analytics"
    )

    c.save()
    return file_name

# -------------------------------------------------
# PDF BUTTON
# -------------------------------------------------
if st.button("Generate Vehicle Health Report (PDF)"):
    pdf = generate_pdf(affected_parts, advisories, prob_dict)
    with open(pdf, "rb") as f:
        st.download_button(
            "Download PDF Report",
            f,
            file_name=pdf,
            mime="application/pdf"
        )
