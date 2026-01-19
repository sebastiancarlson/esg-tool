import pandas as pd
from datetime import datetime

# Schablonfaktorer (kg CO2e per SEK exkl moms)
# Baserat på uppskattade branschsnitt (SCB/Naturvårdsverket input-output)
# Dessa bör uppdateras årligen med inflation
EMISSION_FACTORS = {
    'IT-hårdvara (Laptops, Skärmar)': 0.045,
    'IT-tjänster & Licenser': 0.004,
    'Kontorsmaterial & Förbrukning': 0.025,
    'Marknadsföring & Tryck': 0.015,
    'Konsulttjänster (Management/HR)': 0.003,
    'Möbler & Inredning': 0.035,
    'Städtjänster & Facility': 0.010,
    'Övrigt': 0.010
}

def get_categories():
    return list(EMISSION_FACTORS.keys())

def calculate_co2_from_spend(category, spend_sek):
    """
    Beräknar CO2 baserat på spend och kategori.
    Returnerar (ton_co2, faktor_använd).
    """
    factor = EMISSION_FACTORS.get(category, 0.010)
    co2_kg = spend_sek * factor
    return co2_kg / 1000.0, factor 

def add_spend_item(conn, category, subcategory, spend_sek, period, quality='Estimated'):
    """
    Lägger till en spend-post i databasen och räknar ut CO2.
    """
    co2_tonnes, factor = calculate_co2_from_spend(category, spend_sek)
    
    conn.execute("""
        INSERT INTO f_Scope3_Calculations 
        (category, subcategory, spend_sek, emission_factor, co2e_tonnes, data_quality, reporting_period, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, subcategory, spend_sek, factor, co2_tonnes, quality, period, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    return co2_tonnes

def get_all_items(conn, period=None):
    query = "SELECT * FROM f_Scope3_Calculations"
    if period:
        query += f" WHERE reporting_period = '{period}'"
    return pd.read_sql(query, conn)

def get_spend_summary(conn, period):
    return pd.read_sql(f"""
        SELECT category, SUM(spend_sek) as total_sek, SUM(co2e_tonnes) as total_co2 
        FROM f_Scope3_Calculations 
        WHERE reporting_period = '{period}'
        GROUP BY category
    """, conn)
