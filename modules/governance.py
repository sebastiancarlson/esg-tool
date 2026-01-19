import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

@st.cache_data(ttl=60)
def get_policies():
    try:
        with get_conn() as conn:
            return pd.read_sql("SELECT * FROM f_Governance_Policies ORDER BY next_review_date ASC", conn)
    except: return pd.DataFrame()

def add_policy(name, version, owner, last_updated, esrs_req, doc_link=None):
    if isinstance(last_updated, str):
        date_obj = datetime.strptime(last_updated, '%Y-%m-%d')
    else:
        date_obj = datetime.combine(last_updated, datetime.min.time())
        
    next_review = date_obj + timedelta(days=365)
    
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO f_Governance_Policies 
            (policy_name, document_version, owner, last_updated, next_review_date, esrs_requirement, is_implemented, document_link) 
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (name, version, owner, date_obj.strftime('%Y-%m-%d'), next_review.strftime('%Y-%m-%d'), esrs_req, doc_link))
        conn.commit()
    st.cache_data.clear()

def delete_policy(policy_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM f_Governance_Policies WHERE id = ?", (policy_id,))
        conn.commit()
    st.cache_data.clear()