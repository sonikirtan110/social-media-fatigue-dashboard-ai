import pandas as pd
import mysql.connector  # Added missing import
from config import DB_CONFIG

def export_to_csv():
    # Establish connection using DB_CONFIG
    conn = mysql.connector.connect(**DB_CONFIG)
    query = "SELECT * FROM predictions"
    # Read the SQL query result into a DataFrame
    df = pd.read_sql(query, conn)
    # Export the DataFrame to a CSV file named 'powerbi_data.csv'
    df.to_csv('powerbi_data.csv', index=False)
    conn.close()
    print("Data exported successfully to powerbi_data.csv")

if __name__ == '__main__':
    export_to_csv()
