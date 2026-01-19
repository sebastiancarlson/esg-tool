import pandas as pd

def ensure_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS f_Energi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ar INTEGER,
            manad INTEGER,
            anlaggning_id TEXT,
            el_kwh REAL,
            fjarrvarme_kwh REAL,
            el_kalla TEXT, -- 'Förnybar', 'Mix', 'Kärnkraft'
            scope2_location_based_kg REAL,
            scope2_market_based_kg REAL
        )
    """)
    conn.commit()

def get_grid_mix_factor(year):
    # Nordic Residual Mix (g CO2/kWh) - Exempel
    # 2023: ca 300-400g om ej ursprungsgarantier
    # Svensk medelmix: ca 40g
    return 0.040 # 40g/kWh (Svensk mix - Location Based)

def get_market_based_factor(source):
    if source == 'Förnybar':
        return 0.0
    elif source == 'Kärnkraft':
        return 0.006 # ca 6g/kWh livscykel
    elif source == 'Mix':
        return 0.350 # Residualmix (konservativt)
    else:
        return 0.350

def recalculate_all(conn):
    ensure_tables(conn)
    
    try:
        df = pd.read_sql("SELECT * FROM f_Energi", conn)
        
        updates = []
        for _, row in df.iterrows():
            # Location based (Svensk medel)
            loc_factor = get_grid_mix_factor(row['ar'])
            loc_co2 = (row['el_kwh'] * loc_factor) + (row['fjarrvarme_kwh'] * 0.060) # 60g/kWh schablon fjärrvärme
            
            # Market based (Avtal)
            mark_factor = get_market_based_factor(row['el_kalla'])
            mark_co2 = (row['el_kwh'] * mark_factor) + (row['fjarrvarme_kwh'] * 0.060) # Antar mix för fjärrvärme om ej specat
            
            updates.append((loc_co2, mark_co2, row['id']))
            
        if updates:
            conn.executemany("""
                UPDATE f_Energi 
                SET scope2_location_based_kg = ?, scope2_market_based_kg = ? 
                WHERE id = ?
            """, updates)
            conn.commit()
            
    except Exception as e:
        print(f"Scope 2 Recalculation Error: {e}")
