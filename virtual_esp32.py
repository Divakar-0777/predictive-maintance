from flask import Flask, jsonify
import random

app = Flask(__name__)

def generate_sensor_data():
    # 1. Generate Primary Variable: Oil Temperature (70 - 125 C)
    # We use a weighted distribution to make "Healthy" (lower temps) more common
    oil_temp = int(random.triangular(70, 125, 85))

    # 2. Calculate Correlated Variables (Physics-based)
    
    # Oil Pressure: Inversely proportional to temperature
    # Healthy (85C) -> ~4.0 bar, Critical (120C) -> ~2.0 bar
    # Base calculation with some random noise
    oil_pressure = max(1.0, 6.5 - (0.04 * oil_temp) + random.uniform(-0.3, 0.3))

    # Coolant Temperature: Correlated with Oil Temp
    # Usually slightly higher than oil temp in this simulation context
    coolant_temp = oil_temp + random.randint(5, 15)

    # 3. Generate Other Variables (Loosely correlated or Independent)
    
    # RPM: Higher RPM often correlates with higher temps (stress)
    if oil_temp > 100:
        rpm = random.randint(2200, 3500) # High stress
    else:
        rpm = random.randint(800, 2200)  # Normal operation

    # Fuel Pressure: Random but drops under extreme stress
    if oil_temp > 110:
        fuel_pressure = random.uniform(4.0, 9.0)
    else:
        fuel_pressure = random.uniform(9.0, 16.0)

    # Battery Voltage: Random fluctuation
    battery_voltage = random.uniform(11.5, 13.5)
    if oil_temp > 115: # Extreme heat might affect battery efficiency
        battery_voltage -= random.uniform(0.5, 1.5)

    # 4. Determine Condition based on Generated Values
    if oil_temp > 105 or coolant_temp > 110 or oil_pressure < 2.5:
        condition = "Critical"
    elif oil_temp > 90 or coolant_temp > 95 or oil_pressure < 3.5:
        condition = "Warning"
    else:
        condition = "Healthy"

    return {
        "engine_rpm": rpm,
        "battery_voltage": round(battery_voltage, 2),
        "lub_oil_pressure": round(oil_pressure, 2),
        "fuel_pressure": round(fuel_pressure, 2),
        "coolant_pressure": round(random.uniform(2.0, 5.0), 2),
        "lub_oil_temp": oil_temp,
        "coolant_temp": coolant_temp,
        "label": condition
    }

@app.route('/sensor', methods=['GET'])
def sensor():
    data = generate_sensor_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

