from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os
import mysql.connector
from config import DB_CONFIG  # DB_CONFIG must be defined in config.py

app = Flask(__name__)
CORS(app)

# Load the trained model
MODEL_PATH = "fatigue_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file {MODEL_PATH} not found.")
model = joblib.load(MODEL_PATH)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def log_prediction(data, prediction, category):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO predictions 
        (age, social_media_time, screen_time, platform, prediction, category)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get('Age'),
            data.get('SocialMediaTime'),
            data.get('ScreenTime'),
            data.get('PrimaryPlatform'),
            prediction,
            category
        )
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        print("Database error:", str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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
        # Use cleaned platform value (handle typos)
        platform = input_data['PrimaryPlatform'].replace("Instgram", "Instagram").replace("Youtube", "YouTube")
        recommendations.append(platform_advice.get(platform, "Take regular 5-minute breaks"))
        # Sleep Quality Correlation
        if fatigue_level > 6:
            recommendations.append("💤 Improve sleep quality with digital detox 1 hour before bed")
        return recommendations[:3]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_route():
    try:
        # Validate that request is JSON
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
        platform = platform.replace('Instgram', 'Instagram').replace('Youtube', 'YouTube')
        
        # Prepare input data with defaults (for any missing optional fields)
        input_data = {
            'Age': data['Age'],
            'SocialMediaTime': data['SocialMediaTime'],
            'ScreenTime': data['ScreenTime'],
            'PrimaryPlatform': platform
        }
        
        # Create DataFrame for prediction
        input_df = pd.DataFrame([input_data])
        
        # Make prediction
        prediction_value = model.predict(input_df)[0]
        category = get_fatigue_category(prediction_value)
        
        # Log prediction to MySQL
        log_prediction(input_data, prediction_value, category)
        
        # Generate recommendations
        recommendations = FatigueAdvisor.generate_recommendations(input_data, prediction_value)
        
        return jsonify({
            "Fatigue Category": category,
            "Predicted Fatigue Level": round(float(prediction_value), 2),
            "Recommendations": recommendations
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
