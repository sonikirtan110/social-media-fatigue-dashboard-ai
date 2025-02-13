from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os

app = Flask(__name__)
CORS(app)

# Load your pickle model. Ensure the file exists in your working directory.
model_path = "fatigue_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file {model_path} not found.")
model = joblib.load(model_path)

# Global variable for storing the latest prediction.
latest_prediction = {}

def get_fatigue_category(prediction):
    if prediction <= 3.0:
        return "Better"
    elif prediction <= 5.0:
        return "Good"
    elif prediction <= 7.0:
        return "Average"
    elif prediction <= 9.0:
        return "High"
    else:
        return "Critical"


@app.route('/predict', methods=['POST'])
def predict():
    global latest_prediction
    try:
        # Try to read incoming JSON data; use silent=True so that if parsing fails, data is None.
        data = request.get_json(silent=True)
        
        # If no data (or empty JSON {}) is provided, return the last stored prediction.
        if data is None or data == {}:
            if latest_prediction:
                return jsonify(latest_prediction.get("output", {}))
            else:
                return jsonify({"error": "No prediction available. Provide input data."}), 400

        # Expected columns with default values.
        expected_columns = {
            "Age": 0, 
            "SocialMediaTime": 0, 
            "ScreenTime": 0, 
            "PrimaryPlatform": "Other",
            "EntertainmentSpending": 0, 
            "SocialIsolation": 0, 
            "MessagingTime": 0, 
            "VideoTime": 0,
            "ScreenTimePerNotification": 0, 
            "MusicTime": 0, 
            "TechSavviness": 0, 
            "GamingTime": 0,
            "EntertainmentPlatform": "Unknown", 
            "PreferredDevice": "Unknown", 
            "SleepQuality": 5,
            "TotalEntertainmentTime": 0, 
            "SocialMediaGoal": "None"
        }

        # Merge defaults into data if keys are missing.
        for key, default in expected_columns.items():
            if key not in data:
                data[key] = default

        # Convert data to DataFrame (adjust column ordering as your model expects).
        input_df = pd.DataFrame([data])
        
        # Get the prediction from the model.
        prediction_value = model.predict(input_df)[0]

        # Update the global prediction variable.
        latest_prediction = {
            "input": data,
            "output": {
                "predicted_fatigue_level": round(float(prediction_value),2),
                "fatigue_category": get_fatigue_category(prediction_value)
            }
        }
        # Return only the output part.
        return jsonify(latest_prediction["output"])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)