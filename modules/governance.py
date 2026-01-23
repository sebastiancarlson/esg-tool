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

# --- GAP ANALYSIS FUNCTIONS ---

def get_gap_analysis():
    """
    Fetches all ESRS requirements joined with their GAP status.
    """
    with get_conn() as conn:
        # Left join to show all requirements even if not yet in GAP table
        sql = """
        SELECT r.esrs_code, r.disclosure_requirement, r.description, 
               g.status, g.owner, g.evidence_link, g.notes, g.last_updated
        FROM f_ESRS_Requirements r
        LEFT JOIN f_GAP_Analysis g ON r.esrs_code = g.esrs_code
        ORDER BY r.esrs_code
        """
        df = pd.read_sql(sql, conn)
        # Fill None status with "Not Started"
        df["status"] = df["status"].fillna("Not Started")
        return df

def update_gap_status(esrs_code, status, owner=None, link=None, notes=None):
    """
    Updates the status of a specific ESRS requirement.
    """
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO f_GAP_Analysis (esrs_code, status, owner, evidence_link, notes, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(esrs_code) DO UPDATE SET
                status = excluded.status,
                owner = COALESCE(excluded.owner, owner),
                evidence_link = COALESCE(excluded.evidence_link, evidence_link),
                notes = COALESCE(excluded.notes, notes),
                last_updated = excluded.last_updated
        """, (esrs_code, status, owner, link, notes, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
    st.cache_data.clear()

def get_readiness_kpis():
    """
    Calculates completion % based on GAP status.
    """
    df = get_gap_analysis()
    if df.empty:
        return 0, 0, 0
    
    total = len(df)
    completed = len(df[df["status"].isin(["Compliant", "Completed"])])
    in_progress = len(df[df["status"] == "In Progress"])
    
    score = (completed / total * 100) if total > 0 else 0
    return score, completed, total
