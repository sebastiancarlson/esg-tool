import pandas as pd

def get_hr_summary(conn, year):
    """Hämtar sammanställning av HR-data för ett specifikt år."""
    try:
        return pd.read_sql(f"SELECT * FROM f_HR_Arsdata WHERE ar = {year}", conn)
    except:
        return pd.DataFrame()

def save_extended_hr_data(conn, data_dict):
    """Sparar utökad HR-data enligt ESRS-krav."""
    
    conn.execute("""
        INSERT OR REPLACE INTO f_HR_Arsdata 
        (ar, enps_intern, cnps_konsult, antal_interna, antal_konsulter, nyanstallda_ar, 
         sjukfranvaro_procent, arbetsolyckor_antal, inspirerade_barn_antal, 
         utbildning_timmar_snitt, employee_category, gender_pay_gap_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data_dict['ar'],
        data_dict['enps_intern'],
        data_dict['cnps_konsult'],
        data_dict['antal_interna'],
        data_dict['antal_konsulter'],
        data_dict['nyanstallda_ar'],
        data_dict['sjukfranvaro_procent'],
        data_dict['arbetsolyckor_antal'],
        data_dict['inspirerade_barn_antal'],
        data_dict['utbildning_timmar_snitt'],
        data_dict['employee_category'],
        data_dict['gender_pay_gap_pct']
    ))
    conn.commit()

def add_social_metric(conn, metric_type, value, period, source, category):
    """Lägger till ett specifikt socialt mätetal."""
    conn.execute("""
        INSERT INTO f_Social_Metrics (metric_type, value, period, data_source, employee_category)
        VALUES (?, ?, ?, ?, ?)
    """, (metric_type, value, period, source, category))
    conn.commit()
