from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import mysql.connector
from config import DB_CONFIG
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load model
try:
    model = joblib.load('fatigue_model.pkl')
except Exception as e:
    logger.error(f"Model loading failed: {str(e)}")
    raise

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return None

def log_prediction(data, prediction, category):
    conn = get_db_connection()
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
                round(float(prediction), 2),
                category
            )
            cursor.execute(query, values)
            conn.commit()
            logger.info("Prediction logged successfully")
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

# ... [Keep other functions unchanged] ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
