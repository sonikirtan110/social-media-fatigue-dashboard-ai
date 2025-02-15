from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Load the trained model
MODEL_PATH = "fatigue_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file {MODEL_PATH} not found.")
model = joblib.load(MODEL_PATH)

# Global variable to store the latest prediction
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
        # Screen Time Recommendations
        if input_data['ScreenTime'] > 8:
            recommendations.append("🔅 Reduce daily screen time by 2 hours")
        # Clean up platform value
        platform = input_data['PrimaryPlatform'].replace("Instgram", "Instagram").replace("Youtube", "YouTube")
        platform_advice = {
            'Instagram': "Try using grayscale mode to reduce visual stimulation",
            'YouTube': "Enable reminder breaks every 45 minutes of viewing",
            'TikTok': "Activate screen time management in app settings"
        }
        recommendations.append(platform_advice.get(platform, "Take regular 5-minute breaks"))
        # Sleep Quality Suggestion
        if fatigue_level > 6:
            recommendations.append("💤 Improve sleep quality with digital detox 1 hour before bed")
        return recommendations[:3]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST', 'GET'])
def predict_route():
    global latest_prediction
    try:
        if request.method == 'POST':
            # POST method: Accept new prediction input
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 415

            data = request.get_json()

            # Validate required fields
            required_fields = ['Age', 'SocialMediaTime', 'ScreenTime', 'PrimaryPlatform']
            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

            # Clean up platform field
            platform = data.get('PrimaryPlatform', 'Other')
            platform = platform.replace("Instgram", "Instagram").replace("Youtube", "YouTube")
            input_data = {
                'Age': data['Age'],
                'SocialMediaTime': data['SocialMediaTime'],
                'ScreenTime': data['ScreenTime'],
                'PrimaryPlatform': platform
            }

            # Create DataFrame for prediction
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

        else:  # GET method: return the latest stored prediction
            if latest_prediction:
                return jsonify(latest_prediction)
            else:
                return jsonify({"error": "No prediction available. Please POST input data first."}), 404

    except Exception as e:
        logging.error(f"Error in prediction: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
