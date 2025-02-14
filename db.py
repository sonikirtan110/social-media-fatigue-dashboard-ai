import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

def create_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def initialize_database():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    age INT,
                    social_media_time FLOAT,
                    screen_time FLOAT,
                    platform VARCHAR(50),
                    prediction FLOAT,
                    category VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            cursor.close()
            conn.close()
