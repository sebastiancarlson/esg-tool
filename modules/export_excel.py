import pandas as pd

def create_audit_excel(conn, year):
    # Dummy implementation
    df = pd.DataFrame({'Data': ['Exempeldata']})
    filename = f"ESG_Audit_{year}.xlsx"
    df.to_excel(filename)
    return filename