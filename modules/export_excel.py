import pandas as pd
import os
from datetime import datetime

def create_audit_excel(conn, year):
    """
    Exporterar all relevant data för revision till en Excel-fil
    """
    filename = f"ESG_Audit_{year}.xlsx" # Förenklat namn för enklare download handling
    
    # Lista på tabeller att exportera
    tables = [
        'f_HR_Arsdata',
        'f_Pendling_Beraknad',
        'f_Drivmedel',
        'f_Energi',
        'f_Governance_Inkop',
        'f_Vasentlighet',
        'f_Uppdrag',
        'd_Personal',
        'd_Kundsiter'
    ]
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Översiktsflik
            summary = pd.DataFrame({
                'Rapport': ['ESG Audit Export'],
                'År': [year],
                'Genererad': [datetime.now().strftime('%Y-%m-%d %H:%M')],
                'System': ['ESG Tool v2.0']
            })
            summary.to_excel(writer, sheet_name='Info', index=False)
            
            for table in tables:
                try:
                    # Läs data säkert
                    query = f"SELECT * FROM {table}"
                    
                    # Försök filtrera på år om kolumnen finns (Detta är en förenkling, egentligen borde man kolla schema)
                    # Här läser vi allt för audit trail, enklare och säkrare
                    
                    try:
                        df = pd.read_sql(query, conn)
                        if not df.empty:
                            df.to_excel(writer, sheet_name=table[:31], index=False)
                    except:
                        pass # Tabellen kanske inte finns
                        
                except Exception as e:
                    pass
    except Exception as e:
        # Fallback om något går fel (t.ex. permissions)
        return None
                
    return filename
