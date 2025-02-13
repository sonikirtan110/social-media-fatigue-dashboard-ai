import mysql.connector
from config import DB_CONFIG

def verify_records():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM predictions")
        count = cursor.fetchone()[0]
        print(f"Total records in database: {count}")
        
        # Show latest 5 records
        cursor.execute("""
            SELECT age, social_media_time, screen_time, platform, prediction, category, timestamp 
            FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        print("\nLatest 5 records:")
        for row in cursor.fetchall():
            print(f"Age: {row[0]} | Screen Time: {row[2]}h | Platform: {row[3]} | Prediction: {row[4]} | Category: {row[5]} | Time: {row[6]}")
            
    except Exception as e:
        print(f"Verification failed: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    verify_records()
