import pandas as pd
import streamlit as st
import sqlite3
import os

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

@st.cache_data(ttl=600)
def get_esrs_index(year):
    with get_conn() as conn:
        reqs = pd.read_sql("SELECT * FROM f_ESRS_Requirements", conn)
        status_list = []
        for _, req in reqs.iterrows():
            code, stat, comm = req['esrs_code'], "❌ Saknas", "Ingen data."
            try:
                if code == "E1-6":
                    c = conn.execute(f"SELECT (SELECT COUNT(*) FROM f_Drivmedel WHERE strftime('%Y', datum) = '{year}') + (SELECT COUNT(*) FROM f_Energi WHERE ar = {year}) + (SELECT COUNT(*) FROM f_Scope3_Calculations WHERE reporting_period = '{year}')").fetchone()[0]
                    if c > 0: stat, comm = "✅ Rapporterad", f"Data finns ({c} poster)."
                elif code == "S1-16":
                    gap = conn.execute(f"SELECT gender_pay_gap_pct FROM f_HR_Arsdata WHERE ar = {year}").fetchone()
                    if gap and gap[0]: stat, comm = "✅ Rapporterad", f"Lönegap: {gap[0]}%."
                elif code.startswith("G1"):
                    pol = conn.execute(f"SELECT COUNT(*) FROM f_Governance_Policies WHERE esrs_requirement LIKE '{code[:2]}%'").fetchone()[0]
                    if pol > 0: stat, comm = "✅ Rapporterad", f"{pol} dokument."
            except: pass
            status_list.append({"Kod": code, "Krav": req['disclosure_requirement'], "Status": stat, "Kommentar": comm})
        return pd.DataFrame(status_list)

def calculate_readiness_score(df):
    if df.empty: return 0
    return round(((len(df[df['Status'] == "✅ Rapporterad"]) + (len(df[df['Status'] == "⚠️ Delvis"]) * 0.5)) / len(df)) * 100, 1)
