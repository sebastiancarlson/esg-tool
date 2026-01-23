import pandas as pd
import sqlite3

def add_detailed_waste_record(conn, date, category, is_hazardous, weight, method, supplier):
    """Adds a new detailed waste record."""
    conn.execute("""
        INSERT INTO f_Waste_Detailed 
        (date, waste_category, is_hazardous, weight_kg, treatment_method, supplier)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, category, 1 if is_hazardous else 0, weight, method, supplier))
    conn.commit()

def get_detailed_waste_data(conn):
    """Fetches all detailed waste records."""
    return pd.read_sql("SELECT * FROM f_Waste_Detailed ORDER BY date DESC", conn)

def calculate_waste_metrics(df):
    """Calculates summary metrics for waste."""
    if df.empty:
        return {"total_weight": 0, "recycling_rate": 0, "hazardous_pct": 0}
    
    total_weight = df["weight_kg"].sum()
    hazardous_weight = df[df["is_hazardous"] == 1]["weight_kg"].sum()
    
    # Recycling includes Reuse and Recycling methods
    recovered_weight = df[df["treatment_method"].isin(['Återvinning', 'Reuse'])]["weight_kg"].sum()
    
    recycling_rate = (recovered_weight / total_weight * 100) if total_weight > 0 else 0
    hazardous_pct = (hazardous_weight / total_weight * 100) if total_weight > 0 else 0
    
    return {
        "total_weight": total_weight,
        "recycling_rate": recycling_rate,
        "hazardous_pct": hazardous_pct
    }
