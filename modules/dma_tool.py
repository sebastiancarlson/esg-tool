import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime

def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

ESRS_MAP = {
    "Klimat": "E1", "Energi": "E1", "Föroreningar": "E2", "Vatten": "E3", "Biodiversitet": "E4", "Cirkulär ekonomi": "E5",
    "Egen personal": "S1", "Arbetsvillkor": "S1", "Arbetstagare i värdekedjan": "S2", "Leverantörer": "S2",
    "Berörda samhällen": "S3", "Konsumenter": "S4", "Affärsetik": "G1", "Governance": "G1"
}

@st.cache_data(ttl=60)
def get_dma_data():
    try:
        with get_conn() as conn:
            return pd.read_sql("SELECT * FROM f_DMA_Materiality ORDER BY (impact_score + financial_score) DESC", conn)
    except: return pd.DataFrame()

def add_dma_topic(topic, impact, financial, category):
    esrs_code = "ESRS 2"
    for key, code in ESRS_MAP.items():
        if key.lower() in topic.lower():
            esrs_code = code
            break
    is_material = 1 if (impact >= 3 or financial >= 3) else 0
    
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO f_DMA_Materiality 
            (topic, impact_score, financial_score, esrs_code, category, is_material, created_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic, impact, financial, esrs_code, category, is_material, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
    st.cache_data.clear()

def delete_dma_topic(topic_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM f_DMA_Materiality WHERE id = ?", (topic_id,))
        conn.commit()
    st.cache_data.clear()

# --- IRO FUNCTIONS ---

def add_iro(topic_id, iro_type, description, time_horizon, financial_effect):
    """
    Adds an Impact, Risk, or Opportunity (IRO) to a material topic.
    """
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO f_DMA_IRO (dma_topic_id, type, description, time_horizon, financial_effect)
            VALUES (?, ?, ?, ?, ?)
        """, (topic_id, iro_type, description, time_horizon, financial_effect))
        conn.commit()

def get_iros(topic_id):
    """
    Fetches IROs for a specific topic.
    """
    with get_conn() as conn:
        return pd.read_sql("SELECT * FROM f_DMA_IRO WHERE dma_topic_id = ?", conn, params=(topic_id,))
