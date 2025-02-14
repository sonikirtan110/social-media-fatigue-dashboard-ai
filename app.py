from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import mysql.connector
from config import DB_CONFIG
import logging

app = Flask(__name__)
CORS(app)

# Load the machine learning model
try:
    model = joblib.load('fatigue_model.pkl')
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    raise

# Function to establish MySQL connection
def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"MySQL connection failed: {e}")
        return None

# Function to log prediction to MySQL
def log_prediction(data, prediction, category):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO predictions (age, social_media_time, screen_time, platform, prediction, category)
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
            logging.info("Prediction logged successfully.")
        except Exception as e:
            logging.error(f"Database logging failed: {e}")
        finally:
            cursor.close()
            conn.close()

# Determine fatigue category
def get_fatigue_category(prediction):
    if prediction < 3.5:
        return "Low"
    elif 3.5 <= prediction < 6.5:
        return "Average"
    else:
        return "High"

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Fatigue Prediction API"})

@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Validate required fields
    required_fields = ['Age', 'SocialMediaTime', 'ScreenTime', 'PrimaryPlatform']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        # Prepare data for prediction
        input_df = pd.DataFrame([data])

        # Make prediction
        prediction = model.predict(input_df)[0]
        category = get_fatigue_category(prediction)

        # Log prediction
        log_prediction(data, prediction, category)

        # Response
        return jsonify({
            "Fatigue Category": category,
            "Predicted Fatigue Level": round(float(prediction), 2),
            "Recommendations": generate_recommendations(data, prediction)
        })
    except Exception as e:
        logging.error(f"Prediction failed: {e}")
        return jsonify({"error": str(e)}), 500

def generate_recommendations(input_data, fatigue_level):
    recommendations = []
    if input_data['ScreenTime'] > 6:
        recommendations.append("🔅 Reduce screen time to avoid fatigue.")
    if fatigue_level > 6:
        recommendations.append("💤 Improve sleep with regular breaks.")
    platform_advice = {
        'Instagram': "Use grayscale mode to reduce visual overload.",
        'YouTube': "Set reminder breaks every 45 mins.",
        'TikTok': "Enable app screen time limits."
    }
    platform = input_data['PrimaryPlatform']
    recommendations.append(platform_advice.get(platform, "Take 5-minute breaks every hour."))
    return recommendations

@app.route('/export', methods=['GET'])
def export_to_csv():
    try:
        conn = create_connection()
        if conn:
            query = "SELECT * FROM predictions"
            df = pd.read_sql(query, conn)
            df.to_csv('powerbi_data.csv', index=False)
            conn.close()
            return jsonify({"message": "Data exported to powerbi_data.csv"})
        else:
            return jsonify({"error": "Database connection failed"}), 500
    except Exception as e:
        logging.error(f"CSV export failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
