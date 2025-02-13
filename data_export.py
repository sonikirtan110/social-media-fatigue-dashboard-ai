import pandas as pd
import mysql.connector
from config import DB_CONFIG

def export_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM predictions", conn)
        df.to_csv('predictions_export.csv', index=False)
        print("Exported", len(df), "records to predictions_export.csv")
    except Exception as e:
        print("Export failed:", str(e))

if __name__ == '__main__':
    export_data()
