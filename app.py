from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

MODEL_PATH = "fatigue_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file {MODEL_PATH} not found.")
model = joblib.load(MODEL_PATH)

latest_prediction = None

def get_fatigue_category(prediction):
    if prediction < 3.5:
        return "Low"
    elif 3.5 <= prediction < 6.5:
        return "Average"
    else:
        return "High"

class FatigueAdvisor:
    @staticmethod
    def generate_recommendations(input_data, fatigue_level):
        recommendations = []
        if input_data['ScreenTime'] > 8:
            recommendations.append("🔅 Reduce daily screen time by 2 hours")
        platform = input_data['PrimaryPlatform'].replace("Instgram", "Instagram").replace("Youtube", "YouTube")
        platform_advice = {
            'Instagram': "Try using grayscale mode to reduce visual stimulation",
            'YouTube': "Enable reminder breaks every 45 minutes of viewing",
            'TikTok': "Activate screen time management in app settings"
        }
        recommendations.append(platform_advice.get(platform, "Take regular 5-minute breaks"))
        if fatigue_level > 6:
            recommendations.append("💤 Improve sleep quality with digital detox 1 hour before bed")
        return recommendations[:3]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_route():
    global latest_prediction
    try:
        data = request.get_json()
        required_fields = ['Age', 'SocialMediaTime', 'ScreenTime', 'PrimaryPlatform']
        missing = [field for field in required_fields if field not in data or data[field] == ""]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        platform = data.get('PrimaryPlatform', 'Other').replace("Instgram", "Instagram").replace("Youtube", "YouTube")
        input_data = {
            'Age': int(data['Age']),
            'SocialMediaTime': float(data['SocialMediaTime']),
            'ScreenTime': float(data['ScreenTime']),
            'PrimaryPlatform': platform
        }

        input_df = pd.DataFrame([input_data])
        prediction_value = model.predict(input_df)[0]
        category = get_fatigue_category(prediction_value)
        recommendations = FatigueAdvisor.generate_recommendations(input_data, prediction_value)

        latest_prediction = {
            "fatigue_category": category,
            "predicted_fatigue_level": round(float(prediction_value), 2),
            "Recommendations": recommendations
        }
        return jsonify(latest_prediction)

    except Exception as e:
        logging.error(f"Error in prediction: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
