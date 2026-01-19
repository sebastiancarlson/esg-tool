import pandas as pd
from datetime import datetime

# ESRS Mapping Table based on keywords or categories
ESRS_MAP = {
    "Klimat": "E1",
    "Energi": "E1",
    "Föroreningar": "E2",
    "Vatten": "E3",
    "Biodiversitet": "E4",
    "Cirkulär ekonomi": "E5",
    "Resurshantering": "E5",
    "Egen personal": "S1",
    "Arbetsvillkor": "S1",
    "Arbetstagare i värdekedjan": "S2",
    "Leverantörer": "S2",
    "Berörda samhällen": "S3",
    "Lokalsamhälle": "S3",
    "Konsumenter": "S4",
    "Slutanvändare": "S4",
    "Affärsetik": "G1",
    "Governance": "G1",
    "Anti-korruption": "G1"
}

def get_dma_data(conn):
    """Hämtar all DMA-data sorterad på väsentlighet."""
    try:
        return pd.read_sql("SELECT * FROM f_DMA_Materiality ORDER BY (impact_score + financial_score) DESC", conn)
    except:
        return pd.DataFrame()

def add_dma_topic(conn, topic, impact, financial, category):
    """Lägger till ett ämne i väsentlighetsanalysen."""
    
    # Försök mappa till ESRS kod
    esrs_code = "ESRS 2" # Default
    for key, code in ESRS_MAP.items():
        if key.lower() in topic.lower() or key.lower() in category.lower():
            esrs_code = code
            break
            
    # CSRD-tröskel: Väsentligt om >= 3 på någon av skalorna
    is_material = 1 if (impact >= 3 or financial >= 3) else 0
    
    conn.execute("""
        INSERT INTO f_DMA_Materiality 
        (topic, impact_score, financial_score, esrs_code, category, is_material, created_date, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        topic, 
        impact, 
        financial, 
        esrs_code, 
        category, 
        is_material, 
        datetime.now().strftime('%Y-%m-%d'), 
        datetime.now().strftime('%Y-%m-%d')
    ))
    conn.commit()

def delete_dma_topic(conn, topic_id):
    """Tar bort ett ämne."""
    conn.execute("DELETE FROM f_DMA_Materiality WHERE id = ?", (topic_id,))
    conn.commit()

def get_material_topics(conn):
    """Hämtar endast de ämnen som bedömts som väsentliga."""
    return pd.read_sql("SELECT * FROM f_DMA_Materiality WHERE is_material = 1", conn)
