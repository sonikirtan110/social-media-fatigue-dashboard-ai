import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1978',
    'database': 'social',
    'port': 3310,
    'auth_plugin': 'mysql_native_password'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    if conn.is_connected():
        print("Connection successful!")
    else:
        print("Failed to connect.")
except Exception as e:
    print("Connection error:", e)
finally:
    if conn.is_connected():
        conn.close()
