from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os

# Load the trained model
model = joblib.load('fatigue_prediction_model.pkl')

app = Flask(__name__)
CORS(app)

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
        
        # Platform-specific Advice
        platform_advice = {
            'Instagram': "Try using grayscale mode to reduce visual stimulation",
            'YouTube': "Enable reminder breaks every 45 minutes of viewing",
            'TikTok': "Activate screen time management in app settings"
        }
        recommendations.append(platform_advice.get(input_data['PrimaryPlatform'], "Take regular 5-minute breaks"))
        
        # Sleep Quality Correlation
        if fatigue_level > 6:
            recommendations.append("💤 Improve sleep quality with digital detox 1 hour before bed")
            
        return recommendations[:3]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['Age', 'SocialMediaTime', 'ScreenTime', 'PrimaryPlatform']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Prepare input data with defaults
        input_data = {
            'Age': data['Age'],
            'SocialMediaTime': data['SocialMediaTime'],
            'ScreenTime': data['ScreenTime'],
            'PrimaryPlatform': data['PrimaryPlatform'].replace('Instgram', 'Instagram').replace('Youtube', 'YouTube')
        }

        # Create DataFrame with proper feature engineering
        input_df = pd.DataFrame([input_data])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        
        # Generate recommendations
        recommendations = FatigueAdvisor.generate_recommendations(input_data, prediction)
        
        return jsonify({
            "fatigue_category": get_fatigue_category(prediction),
            "predicted_fatigue_level": round(float(prediction), 2),
            "Recommendations": recommendations
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
