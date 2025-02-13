# db.py
import mysql.connector
from config import DB_CONFIG

def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def initialize_database():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    age INT NOT NULL,
                    social_media_time FLOAT NOT NULL,
                    screen_time FLOAT NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    prediction FLOAT NOT NULL,
                    category VARCHAR(20) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"Initialization error: {str(e)}")
        finally:
            cursor.close()
            conn.close()
