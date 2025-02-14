# db.py
import psycopg2
from config import DB_CONFIG
import logging

def create_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def initialize_database():
    conn = create_connection()
    if conn is None:
        logging.error("Unable to initialize database; connection not established.")
        return
    try:
        cursor = conn.cursor()
        # Create the predictions table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                age INT,
                social_media_time FLOAT,
                screen_time FLOAT,
                platform VARCHAR(50),
                prediction FLOAT,
                category VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
    finally:
        cursor.close()
        conn.close()
