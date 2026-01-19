import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

@st.cache_data(ttl=600)
def get_policies():
    """Hämtar alla policys och beräknar status."""
    try:
        with get_conn() as conn:
            df = pd.read_sql("SELECT * FROM f_Governance_Policies ORDER BY next_review_date ASC", conn)
        
        if df.empty: return df
        
        today = datetime.now().date()
        def get_status(date_str):
            if not date_str: return "🔴 Okänt"
            try:
                review_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if review_date < today: return "🔴 Utgången"
                elif review_date < (today + timedelta(days=90)): return "🟡 Snart dags"
                else: return "🟢 OK"
            except: return "🔴 Fel datum"

        df['Status'] = df['next_review_date'].apply(get_status)
        return df
    except: return pd.DataFrame()

def add_policy(conn, name, version, owner, last_updated, esrs_req):
    if isinstance(last_updated, str):
        date_obj = datetime.strptime(last_updated, '%Y-%m-%d')
    else:
        date_obj = datetime.combine(last_updated, datetime.min.time())
        
    next_review = date_obj + timedelta(days=365)
    
    conn.execute("INSERT INTO f_Governance_Policies (policy_name, document_version, owner, last_updated, next_review_date, esrs_requirement, is_implemented) VALUES (?, ?, ?, ?, ?, ?, 1)", (name, version, owner, date_obj.strftime('%Y-%m-%d'), next_review.strftime('%Y-%m-%d'), esrs_req))
    conn.commit()
    st.cache_data.clear()

def delete_policy(conn, policy_id):
    conn.execute("DELETE FROM f_Governance_Policies WHERE id = ?", (policy_id,))
    conn.commit()
    st.cache_data.clear()
