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
    'Övrigt': 0.010
}

def get_categories(): return list(EMISSION_FACTORS.keys())

def calculate_co2_from_spend(category, spend_sek):
    factor = EMISSION_FACTORS.get(category, 0.010)
    return (spend_sek * factor) / 1000.0, factor

def add_spend_item(conn, category, subcategory, spend_sek, period, quality='Estimated'):
    co2, factor = calculate_co2_from_spend(category, spend_sek)
    conn.execute("INSERT INTO f_Scope3_Calculations (category, subcategory, spend_sek, emission_factor, co2e_tonnes, data_quality, reporting_period, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (category, subcategory, spend_sek, factor, co2, quality, period, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    st.cache_data.clear()
    return co2

@st.cache_data(ttl=600)
def get_all_items(period=None):
    with get_conn() as conn:
        query = "SELECT * FROM f_Scope3_Calculations"
        if period: query += f" WHERE reporting_period = '{period}'"
        return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_spend_summary(period):
    with get_conn() as conn:
        return pd.read_sql(f"SELECT category, SUM(spend_sek) as total_sek, SUM(co2e_tonnes) as total_co2 FROM f_Scope3_Calculations WHERE reporting_period = '{period}' GROUP BY category", conn)
