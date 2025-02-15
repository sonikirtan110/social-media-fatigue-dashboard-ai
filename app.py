from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os
import mysql.connector
from datetime import datetime
from config import DB_CONFIG

app = Flask(__name__)
CORS(app)

# Load the trained model
MODEL_PATH = "fatigue_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file {MODEL_PATH} not found.")
model = joblib.load(MODEL_PATH)

def get_fatigue_category(prediction):
    return next((
        ("Low", 3.5),
        ("Average", 6.5),
        ("High", float('inf'))
    ) for limit in [3.5, 6.5, float('inf')] if prediction < limit)[0][0]

class FatigueAdvisor:
    @staticmethod
    def generate_recommendations(input_data, fatigue_level):
        recommendations = []
        
        # Screen Time Recommendations
        if input_data['ScreenTime'] > 8:
            recommendations.append("🔅 Reduce daily screen time by 2 hours")
        
        # Platform-specific Advice
        platform = input_data['PrimaryPlatform'].replace("Instgram", "Instagram").replace("Youtube", "YouTube")
        platform_advice = {
            'Instagram': "Try using grayscale mode to reduce visual stimulation",
            'YouTube': "Enable reminder breaks every 45 minutes of viewing",
            'TikTok': "Activate screen time management in app settings"
        }
        recommendations.append(platform_advice.get(platform, "Take regular 5-minute breaks"))
        
        # Sleep Quality Correlation
        if fatigue_level > 6:
            recommendations.append("💤 Improve sleep quality with digital detox 1 hour before bed")
        
        return recommendations[:3]

def validate_input(data):
    required = {
        'Age': (int, 1, 120),
        'SocialMediaTime': (float, 0, 24),
        'ScreenTime': (float, 0, 24),
        'PrimaryPlatform': (str, 1, 20)
    }
    
    errors = []
    for field, (dtype, min_val, max_val) in required.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
            continue
            
        try:
            if dtype == int:
                data[field] = int(data[field])
            elif dtype == float:
                data[field] = float(data[field])
            elif dtype == str:
                data[field] = str(data[field]).strip()
                
            if not (min_val <= data[field] <= max_val):
                errors.append(f"{field} must be between {min_val} and {max_val}")
        except ValueError:
            errors.append(f"Invalid type for {field} - expected {dtype.__name__}")
    
    return data, errors

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_route():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        raw_data = request.get_json() or {}
        data, errors = validate_input(raw_data)
        
        if errors:
            return jsonify({
                "error": "Validation failed",
                "details": errors,
                "required_format": {
                    "Age": "integer (1-120)",
                    "SocialMediaTime": "number (0-24)",
                    "ScreenTime": "number (0-24)",
                    "PrimaryPlatform": "string"
                }
            }), 400
        
        # Clean platform name
        data['PrimaryPlatform'] = data['PrimaryPlatform'].replace('Instgram', 'Instagram').replace('Youtube', 'YouTube')
        
        # Create DataFrame with proper data types
        input_df = pd.DataFrame([{
            'Age': int(data['Age']),
            'SocialMediaTime': float(data['SocialMediaTime']),
            'ScreenTime': float(data['ScreenTime']),
            'PrimaryPlatform': data['PrimaryPlatform']
        }])
        
        # Make prediction
        prediction_value = model.predict(input_df)[0]
        category = get_fatigue_category(prediction_value)
        
        # Generate recommendations
        recommendations = FatigueAdvisor.generate_recommendations({
            'ScreenTime': data['ScreenTime'],
            'PrimaryPlatform': data['PrimaryPlatform']
        }, prediction_value)
        
        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "fatigue_category": category,
            "predicted_fatigue_level": round(float(prediction_value), 2),
            "Recommendations": recommendations
        })
    
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
