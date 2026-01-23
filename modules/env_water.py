import pandas as pd
import sqlite3

def add_water_record(conn, date, withdrawal, source, discharge, dest, recycled):
    """Adds a new water record to the database."""
    consumption = withdrawal - discharge
    conn.execute("""
        INSERT INTO f_Water_Data 
        (date, withdrawal_m3, withdrawal_source, discharge_m3, discharge_dest, consumption_m3, recycled_m3)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, withdrawal, source, discharge, dest, consumption, recycled))
    conn.commit()

def get_water_data(conn):
    """Fetches all water data records."""
    return pd.read_sql("SELECT * FROM f_Water_Data ORDER BY date DESC", conn)

def calculate_water_metrics(df):
    """Calculates summary metrics for water usage."""
    if df.empty:
        return {"total_withdrawal": 0, "total_consumption": 0, "recycling_rate": 0}
    
    total_withdrawal = df["withdrawal_m3"].sum()
    total_consumption = df["consumption_m3"].sum()
    total_recycled = df["recycled_m3"].sum()
    
    recycling_rate = (total_recycled / total_withdrawal * 100) if total_withdrawal > 0 else 0
    
    return {
        "total_withdrawal": total_withdrawal,
        "total_consumption": total_consumption,
        "recycling_rate": recycling_rate
    }
