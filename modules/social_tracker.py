import pandas as pd
import streamlit as st
import sqlite3
import os

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

@st.cache_data(ttl=600)
def get_hr_summary(year):
    try:
        with get_conn() as conn:
            return pd.read_sql(f"SELECT * FROM f_HR_Arsdata WHERE ar = {year}", conn)
    except: return pd.DataFrame()

def save_extended_hr_data(conn, data):
    conn.execute("INSERT OR REPLACE INTO f_HR_Arsdata (ar, enps_intern, cnps_konsult, antal_interna, antal_konsulter, nyanstallda_ar, sjukfranvaro_procent, arbetsolyckor_antal, inspirerade_barn_antal, utbildning_timmar_snitt, employee_category, gender_pay_gap_pct) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data['ar'], data['enps_intern'], data['cnps_konsult'], data['antal_interna'], data['antal_konsulter'], data['nyanstallda_ar'], data['sjukfranvaro_procent'], data['arbetsolyckor_antal'], data['inspirerade_barn_antal'], data['utbildning_timmar_snitt'], data['employee_category'], data['gender_pay_gap_pct']))
    conn.commit()
    st.cache_data.clear()
