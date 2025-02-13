import pandas as pd
from db import create_connection

def export_to_csv(filename='predictions.csv'):
    conn = create_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT * FROM predictions", conn)
            df.to_csv(filename, index=False)
            print(f"Exported {len(df)} records to {filename}")
        except Exception as e:
            print(f"Export error: {str(e)}")
        finally:
            conn.close()

if __name__ == '__main__':
    export_to_csv()
