import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

EMISSION_FACTORS = {
    'IT-hårdvara (Laptops, Skärmar)': 0.045,
    'IT-tjänster & Licenser': 0.004,
    'Kontorsmaterial & Förbrukning': 0.025,
    'Marknadsföring & Tryck': 0.015,
    'Konsulttjänster (Management/HR)': 0.003,
    'Möbler & Inredning': 0.035,
    'Städtjänster & Facility': 0.010,
    'Resor (Tåg/Flyg/Hotell)': 0.020,
    'Livsmedel: Kaffe/Te': 0.040,
    'Livsmedel: Mjölk/Mejeri': 0.030,
    'Livsmedel: Frukt/Grönt': 0.010,
    'Livsmedel: Bröd/Kakor': 0.015,
    'Livsmedel: Kött/Chark': 0.060,
    'Livsmedel: Måltider/Catering': 0.025,
    'Övrigt': 0.010
}

def get_categories(): return list(EMISSION_FACTORS.keys())

def add_spend_item(category, subcategory, product_name, spend_sek, period, quality='Estimated'):
    factor = EMISSION_FACTORS.get(category, 0.010)
    co2 = (spend_sek * factor) / 1000.0
    
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO f_Scope3_Calculations 
            (category, subcategory, product_name, spend_sek, emission_factor, co2e_tonnes, data_quality, reporting_period, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, subcategory, product_name, spend_sek, factor, co2, quality, period, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
    st.cache_data.clear()
    return co2

@st.cache_data(ttl=60)
def get_spend_summary(period):
    with get_conn() as conn:
        return pd.read_sql(f"SELECT category, SUM(spend_sek) as total_sek, SUM(co2e_tonnes) as total_co2 FROM f_Scope3_Calculations WHERE reporting_period = '{period}' GROUP BY category", conn)

@st.cache_data(ttl=60)
def get_product_breakdown(period):
    with get_conn() as conn:
        try:
            return pd.read_sql(f"SELECT product_name, category, SUM(co2e_tonnes) as co2 FROM f_Scope3_Calculations WHERE reporting_period = '{period}' AND product_name != '' GROUP BY product_name, category ORDER BY co2 DESC", conn)
        except: return pd.DataFrame()
