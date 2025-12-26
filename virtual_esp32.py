# virtual_esp32.py
import random

def get_sensor_data():
    oil_temp = int(random.triangular(70, 125, 85))
    oil_pressure = max(1.0, 6.5 - (0.04 * oil_temp) + random.uniform(-0.3, 0.3))
    coolant_temp = oil_temp + random.randint(5, 15)

    rpm = random.randint(2200, 3500) if oil_temp > 100 else random.randint(800, 2200)
    fuel_pressure = random.uniform(4.0, 9.0) if oil_temp > 110 else random.uniform(9.0, 16.0)
    battery_voltage = random.uniform(11.5, 13.5)
    if oil_temp > 115:
        battery_voltage -= random.uniform(0.5, 1.5)

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