import pandas as pd
from datetime import datetime, timedelta
from modules.distance_api import get_distance

def calculate_emissions(distans_km, start, slut, dagar_vecka, fardmedel):
    """
    Beräknar CO2 för ett enskilt uppdrag
    """
    
    # Antal arbetsdagar
    if pd.isna(start) or pd.isna(slut):
        return {
            'total_km': 0,
            'total_co2_kg': 0,
            'datakvalitet': 'Felaktig Data',
            'emissionsfaktor': 0
        }
        
    delta = (slut - start).days
    veckor = delta / 7
    arbetsdagar = int(veckor * dagar_vecka)
    
    # Emissionsfaktorer (kg CO2/km)
    faktorer = {
        'Bil': 0.12,
        'Elbil': 0.02,
        'Buss': 0.04,
        'Tåg': 0.006,
        'Cykel': 0.0,
        'Okänt': 0.08  # Schablon
    }
    
    ef = faktorer.get(fardmedel, 0.08)
    
    # Beräkning
    total_km = distans_km * 2 * arbetsdagar
    co2_kg = total_km * ef
    
    # Datakvalitet
    if fardmedel == 'Okänt':
        kvalitet = 'Schablon'
    elif fardmedel in faktorer:
        kvalitet = 'Verifierad'
    else:
        kvalitet = 'Estimerad'
    
    return {
        'total_km': total_km,
        'total_co2_kg': co2_kg,
        'datakvalitet': kvalitet,
        'emissionsfaktor': ef
    }

def calculate_all_consultants(conn):
    """
    Beräknar alla konsultuppdrag som saknar beräkning
    """
    
    # Ensure tables exist (basic check)
    try:
        uppdrag = pd.read_sql("""
            SELECT 
                u.uppdrag_id,
                u.person_id,
                u.startdatum,
                u.slutdatum,
                u.dagar_per_vecka,
                u.distans_km,
                u.fardmedel,
                p.hem_postnummer,
                k.postnummer as kund_postnummer
            FROM f_Uppdrag u
            JOIN d_Personal p ON u.person_id = p.person_id
            JOIN d_Kundsiter k ON u.kund_plats_id = k.kund_plats_id
            WHERE u.uppdrag_id NOT IN (SELECT uppdrag_id FROM f_Pendling_Beraknad)
        """, conn)
    except Exception as e:
        return {'error': str(e), 'antal_uppdrag': 0, 'total_co2_ton': 0, 'quality_breakdown': {}}
    
    total_co2 = 0
    quality_counts = {'Verifierad': 0, 'Estimerad': 0, 'Schablon': 0, 'Felaktig Data': 0}
    
    for _, row in uppdrag.iterrows():
        # Hämta distans om saknas
        if pd.isna(row['distans_km']):
            distans = get_distance(row['hem_postnummer'], row['kund_postnummer'])
        else:
            distans = row['distans_km']
        
        # Beräkna
        result = calculate_emissions(
            distans,
            pd.to_datetime(row['startdatum']),
            pd.to_datetime(row['slutdatum']),
            row['dagar_per_vecka'],
            row['fardmedel']
        )
        
        # Spara i databas
        try:
            conn.execute("""
                INSERT INTO f_Pendling_Beraknad 
                (uppdrag_id, antal_arbetsdagar, total_km, emissionsfaktor_kg_per_km, totalt_co2_kg, datakvalitet)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row['uppdrag_id'],
                result['total_km'] / (distans * 2) if distans > 0 else 0,  # Återberäkna arbetsdagar
                result['total_km'],
                result['emissionsfaktor'],
                result['total_co2_kg'],
                result['datakvalitet']
            ))
            
            total_co2 += result['total_co2_kg']
            if result['datakvalitet'] in quality_counts:
                quality_counts[result['datakvalitet']] += 1
        except Exception as e:
            print(f"Error saving calculation for uppdrag {row['uppdrag_id']}: {e}")
            pass
    
    conn.commit()
    
    return {
        'antal_uppdrag': len(uppdrag),
        'total_co2_ton': total_co2 / 1000,
        'quality_breakdown': quality_counts
    }