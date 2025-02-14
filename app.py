from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import logging
from db import create_connection, initialize_database

app = Flask(__name__)
CORS(app)

# Initialize database
initialize_database()

# Load model
try:
    model = joblib.load('fatigue_model.pkl')
except Exception as e:
    logging.error(f"Model loading failed: {str(e)}")
    raise

def log_prediction(data, prediction, category):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO predictions 
            (age, social_media_time, screen_time, platform, prediction, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                data['Age'],
                data['SocialMediaTime'],
                data['ScreenTime'],
                data['PrimaryPlatform'],
                round(prediction, 2),
                category
            )
            cursor.execute(query, values)
            conn.commit()
            logging.info("Prediction logged successfully")
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
        finally:
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
            recommendations.append("💤 Improve sleep quality with a digital detox 1 hour before bed")

        return recommendations[:3]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_route():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()
        required_fields = ['Age', 'SocialMediaTime', 'ScreenTime', 'PrimaryPlatform']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        platform = data.get('PrimaryPlatform', 'Other').replace("Instgram", "Instagram").replace("Youtube", "YouTube")

        input_data = {
            'Age': data['Age'],
            'SocialMediaTime': data['SocialMediaTime'],
            'ScreenTime': data['ScreenTime'],
            'PrimaryPlatform': platform
        }

        input_df = pd.DataFrame([input_data])
        prediction_value = model.predict(input_df)[0]
        category = get_fatigue_category(prediction_value)

        log_prediction(input_data, prediction_value, category)
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
