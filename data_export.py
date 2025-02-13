import pandas as pd
import mysql.connector
from config import DB_CONFIG

def export_data():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        query = """
        SELECT 
            id,
            age AS Age,
            social_media_time AS SocialMediaTime,
            screen_time AS ScreenTime,
            platform AS PrimaryPlatform,
            prediction AS PredictedFatigueLevel,
            category AS FatigueCategory,
            timestamp AS PredictionTime
        FROM predictions
        """
        df = pd.read_sql(query, conn)
        df.to_csv('predictions_export.csv', index=False)
        print(f"Exported {len(df)} records successfully!")
        return True
    except Exception as e:
        print(f"Export failed: {str(e)}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    export_data()
