import pandas as pd
import streamlit as st

@st.cache_data(ttl=600)
def get_esrs_index(conn, year):
    """
    Genererar en statuslista över ESRS-krav baserat på tillgänglig data.
    """
    
    requirements = pd.read_sql("SELECT * FROM f_ESRS_Requirements", conn)
    
    # Status check logic
    status_list = []
    
    for _, req in requirements.iterrows():
        code = req['esrs_code']
        status = "❌ Saknas"
        comment = "Ingen data hittades."
        
        if code == "E1-6":
            # Kolla klimatdata
            try:
                c1 = conn.execute(f"SELECT COUNT(*) FROM f_Drivmedel WHERE strftime('%Y', datum) = '{year}'").fetchone()[0]
                c2 = conn.execute(f"SELECT COUNT(*) FROM f_Energi WHERE ar = {year}").fetchone()[0]
                c3 = conn.execute(f"SELECT COUNT(*) FROM f_Scope3_Calculations WHERE reporting_period = '{year}'").fetchone()[0]
                
                if (c1 + c2 + c3) > 0:
                    status = "✅ Rapporterad"
                    comment = f"Data finns för Scope 1, 2 och 3 ({c1+c2+c3} poster)."
                elif (c1 + c2) > 0:
                    status = "⚠️ Delvis"
                    comment = "Data saknas för Scope 3."
            except: pass
            
        elif code == "S1-16":
            # Kolla lönegap
            try:
                gap = conn.execute(f"SELECT gender_pay_gap_pct FROM f_HR_Arsdata WHERE ar = {year}").fetchone()
                if gap and gap[0] > 0:
                    status = "✅ Rapporterad"
                    comment = f"Lönegap registrerat: {gap[0]}%."
            except: pass
            
        elif code.startswith("S1"):
            # Kolla allmän HR-data
            try:
                hr = conn.execute(f"SELECT antal_interna FROM f_HR_Arsdata WHERE ar = {year}").fetchone()
                if hr and hr[0] > 0:
                    status = "✅ Rapporterad"
                    comment = "Grundläggande HR-data finns."
            except: pass
            
        elif code.startswith("G1") or code == "S1-1":
            # Kolla policys
            try:
                pol = conn.execute(f"SELECT COUNT(*) FROM f_Governance_Policies WHERE esrs_requirement LIKE '{code[:2]}%'").fetchone()[0]
                if pol > 0:
                    status = "✅ Rapporterad"
                    comment = f"{pol} styrdokument hittades."
            except: pass
            
        status_list.append({
            "Kod": code,
            "Krav": req['disclosure_requirement'],
            "Status": status,
            "Kommentar": comment
        })
        
    return pd.DataFrame(status_list)

def calculate_readiness_score(index_df):
    """Beräknar Readiness Score i %."""
    if index_df.empty: return 0
    total = len(index_df)
    completed = len(index_df[index_df['Status'] == "✅ Rapporterad"])
    partial = len(index_df[index_df['Status'] == "⚠️ Delvis"])
    
    score = ((completed + (partial * 0.5)) / total) * 100
    return round(score, 1)