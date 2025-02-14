from config import DB_CONFIG
import mysql.connector
import logging

def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("Database connection successful.")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def initialize_database():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
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
