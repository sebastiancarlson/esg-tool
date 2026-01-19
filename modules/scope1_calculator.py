import pandas as pd

def ensure_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS f_Drivmedel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT,
            volym_liter REAL,
            drivmedelstyp TEXT,
            co2_kg REAL,
            kvitto_ref TEXT
        )
    """)
    conn.commit()

def get_emission_factor(drivmedel):
    # Schablonvärden kg CO2e per liter (WTW - Well to Wheel om möjligt, annars TTW)
    # Exempelvärden baserade på drivmedelsförordningen/Naturvårdsverket
    faktorer = {
        'Diesel (MK1)': 2.54,
        'Diesel (HVO100)': 0.35, # Varierar kraftigt beroende på råvara, sätter konservativt
        'Bensin (95)': 2.36,
        'Bensin (98)': 2.40,
        'E85': 1.65, # Genomsnitt
        'Biogas': 0.6 # kg/Nm3 ca
    }
    return faktorer.get(drivmedel, 2.5)

def recalculate_all(conn):
    ensure_tables(conn)
    
    try:
        df = pd.read_sql("SELECT * FROM f_Drivmedel", conn)
        
        updates = []
        for _, row in df.iterrows():
            faktor = get_emission_factor(row['drivmedelstyp'])
            new_co2 = row['volym_liter'] * faktor
            updates.append((new_co2, row['id']))
            
        if updates:
            conn.executemany("UPDATE f_Drivmedel SET co2_kg = ? WHERE id = ?", updates)
            conn.commit()
            
    except Exception as e:
        print(f"Scope 1 Recalculation Error: {e}")
