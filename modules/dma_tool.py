import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime

# DB Helper
def get_conn():
    path = "database/esg_index.db"
    if not os.path.exists(path) and os.path.exists(f"../{path}"): path = f"../{path}"
    return sqlite3.connect(path)

# ESRS Mapping Table
ESRS_MAP = {
    "Klimat": "E1", "Energi": "E1", "Föroreningar": "E2", "Vatten": "E3", "Biodiversitet": "E4", "Cirkulär ekonomi": "E5",
    "Egen personal": "S1", "Arbetsvillkor": "S1", "Arbetstagare i värdekedjan": "S2", "Leverantörer": "S2",
    "Berörda samhällen": "S3", "Konsumenter": "S4", "Affärsetik": "G1", "Governance": "G1", "Anti-korruption": "G1"
}

@st.cache_data(ttl=600)
def get_dma_data():
    """Hämtar all DMA-data sorterad på väsentlighet."""
    try:
        with get_conn() as conn:
            return pd.read_sql("SELECT * FROM f_DMA_Materiality ORDER BY (impact_score + financial_score) DESC", conn)
    except:
        return pd.DataFrame()

def add_dma_topic(conn, topic, impact, financial, category):
    """Lägger till ett ämne i väsentlighetsanalysen."""
    # ... (logik oförändrad men tar fortfarande emot conn för skrivning, det är ok då den ej är cachad)
    esrs_code = "ESRS 2"
    for key, code in ESRS_MAP.items():
        if key.lower() in topic.lower() or key.lower() in category.lower():
            esrs_code = code
            break
            
    is_material = 1 if (impact >= 3 or financial >= 3) else 0
    
    conn.execute("""
        INSERT INTO f_DMA_Materiality 
        (topic, impact_score, financial_score, esrs_code, category, is_material, created_date, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (topic, impact, financial, esrs_code, category, is_material, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    st.cache_data.clear()

def delete_dma_topic(conn, topic_id):
    conn.execute("DELETE FROM f_DMA_Materiality WHERE id = ?", (topic_id,))
    conn.commit()
    st.cache_data.clear()

@st.cache_data(ttl=600)
def get_material_topics():
    with get_conn() as conn:
        return pd.read_sql("SELECT * FROM f_DMA_Materiality WHERE is_material = 1", conn)
