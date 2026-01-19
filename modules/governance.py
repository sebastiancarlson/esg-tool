import pandas as pd
from datetime import datetime, timedelta

def get_policies(conn):
    """Hämtar alla policys och beräknar status."""
    try:
        df = pd.read_sql("SELECT * FROM f_Governance_Policies ORDER BY next_review_date ASC", conn)
        
        if df.empty:
            return df
        
        # Beräkna status
        today = datetime.now().date()
        
        def get_status(date_str):
            if not date_str: return "🔴 Okänt"
            try:
                review_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if review_date < today:
                    return "🔴 Utgången"
                elif review_date < (today + timedelta(days=90)):
                    return "🟡 Snart dags"
                else:
                    return "🟢 OK"
            except:
                return "🔴 Fel datum"

        df['Status'] = df['next_review_date'].apply(get_status)
        return df
    except Exception as e:
        return pd.DataFrame()

def add_policy(conn, name, version, owner, last_updated, esrs_req):
    """Lägger till en policy och sätter nästa revidering till +1 år."""
    
    # Beräkna nästa review datum (+1 år)
    if isinstance(last_updated, str):
        date_obj = datetime.strptime(last_updated, '%Y-%m-%d')
    else:
        date_obj = datetime.combine(last_updated, datetime.min.time()) # Konvertera date till datetime
        
    next_review = date_obj + timedelta(days=365)
    
    conn.execute("""
        INSERT INTO f_Governance_Policies 
        (policy_name, document_version, owner, last_updated, next_review_date, esrs_requirement, is_implemented)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (name, version, owner, date_obj.strftime('%Y-%m-%d'), next_review.strftime('%Y-%m-%d'), esrs_req))
    conn.commit()

def delete_policy(conn, policy_id):
    conn.execute("DELETE FROM f_Governance_Policies WHERE id = ?", (policy_id,))
    conn.commit()
