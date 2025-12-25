import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# -------------------------------------------------
# 1. GENERATE SYNTHETIC DATA
# -------------------------------------------------
def generate_synthetic_data(n_samples=1000):
    data = []
    
    for _ in range(n_samples):
        # Logic similar to virtual_esp32.py but with some added variance
        condition = random.choices(
            ["Healthy", "Warning", "Critical"],
            weights=[0.5, 0.3, 0.2]
        )[0]

        if condition == "Healthy":
            oil_temp = random.randint(70, 92)
            coolant_temp = random.randint(75, 98)
            oil_pressure = random.uniform(3.2, 5.5)
            fuel_pressure = random.uniform(9.0, 16.0)
            rpm = random.randint(800, 2200)
            battery_voltage = random.uniform(12.2, 13.5)
            
        elif condition == "Warning":
            oil_temp = random.randint(90, 108)
            coolant_temp = random.randint(95, 115)
            oil_pressure = random.uniform(2.2, 3.5)
            fuel_pressure = random.uniform(7.0, 10.0)
            rpm = random.randint(2000, 2800)
            battery_voltage = random.uniform(11.5, 12.4)

        else:  # Critical
            oil_temp = random.randint(105, 125)
            coolant_temp = random.randint(110, 135)
            oil_pressure = random.uniform(1.0, 2.5)
            fuel_pressure = random.uniform(4.0, 7.5)
            rpm = random.randint(2500, 3500)
            battery_voltage = random.uniform(10.0, 11.8)

        # Add some noise to make it realistic
        oil_temp += random.randint(-2, 2)
        coolant_temp += random.randint(-2, 2)
        oil_pressure += random.uniform(-0.1, 0.1)
        
        # Derived feature: Temp Difference
        temp_diff = abs(oil_temp - coolant_temp)

        data.append({
            "engine_rpm": rpm,
            "lub_oil_pressure": round(oil_pressure, 2),
            "fuel_pressure": round(fuel_pressure, 2),
            "coolant_pressure": round(random.uniform(2.0, 5.0), 2), # Less critical
            "lub_oil_temp": oil_temp,
            "coolant_temp": coolant_temp,
            "battery_voltage": round(battery_voltage, 2),
            "temp_diff": temp_diff,
            "condition": condition
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating synthetic data...")
    df = generate_synthetic_data(2000)
    
    # -------------------------------------------------
    # 2. PREPARE DATA
    # -------------------------------------------------
    X = df.drop("condition", axis=1)
    y = df["condition"]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # -------------------------------------------------
    # 3. TRAIN MODEL
    # -------------------------------------------------
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # -------------------------------------------------
    # 4. EVALUATE
    # -------------------------------------------------
    y_pred = clf.predict(X_test)
    print("\nModel Evaluation:")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    
    # -------------------------------------------------
    # 5. SAVE MODEL
    # -------------------------------------------------
    joblib.dump(clf, "vehicle_health_model.pkl")
    print("\nModel saved as 'vehicle_health_model.pkl'")
