import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1978",
            database="social",
            port=3310  # Default MySQL port (adjust if needed)
        )
        if conn.is_connected():
            print("Connected to MySQL database")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
