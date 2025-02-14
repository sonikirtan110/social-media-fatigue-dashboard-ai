# db.py
import psycopg2
from config import DB_CONFIG
import logging

def create_connection():
    """
    Establish and return a PostgreSQL database connection.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Database connection successful!")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def initialize_database():
    """
    Create the predictions table if it doesn't exist.
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
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
            print("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
        finally:
            cursor.close()
            conn.close()
