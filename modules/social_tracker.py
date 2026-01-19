import pandas as pd
import streamlit as st
import sqlite3
import os

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

@st.cache_data(ttl=60)
def get_hr_summary(year):
    try:
        with get_conn() as conn:
            return pd.read_sql(f"SELECT * FROM f_HR_Arsdata WHERE ar = {year}", conn)
    except: return pd.DataFrame()

def save_extended_hr_data(data):
    """Sparar HR-data. Öppnar egen koppling för att undvika trådningsfel."""
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO f_HR_Arsdata 
            (ar, enps_intern, cnps_konsult, antal_interna, antal_konsulter, nyanstallda_ar, 
             sjukfranvaro_procent, arbetsolyckor_antal, inspirerade_barn_antal, 
             utbildning_timmar_snitt, employee_category, gender_pay_gap_pct, ledning_kvinnor, ledning_man)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('ar'), data.get('enps_intern', 0), data.get('cnps_konsult', 0),
            data.get('antal_interna', 0), data.get('antal_konsulter', 0), data.get('nyanstallda_ar', 0),
            data.get('sjukfranvaro_procent', 0), data.get('arbetsolyckor_antal', 0),
            data.get('inspirerade_barn_antal', 0), data.get('utbildning_timmar_snitt', 0),
            data.get('employee_category', 'Mixed'), data.get('gender_pay_gap_pct', 0),
            data.get('ledning_kvinnor', 0), data.get('ledning_man', 0)
        ))
        conn.commit()
    st.cache_data.clear()