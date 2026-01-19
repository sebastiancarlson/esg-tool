import pandas as pd
from datetime import datetime
import markdown
try:
    from weasyprint import HTML
except ImportError:
    HTML = None

def generate_csrd_report(conn, year):
    """
    Genererar CSRD-rapport enligt ESRS-struktur baserat på den senaste databas-schemat.
    """
    
    # 1. MILJÖDATA (E1)
    try:
        s1 = pd.read_sql(f"SELECT SUM(co2_kg)/1000.0 as ton FROM f_Drivmedel", conn).iloc[0,0] or 0.0
        s2 = pd.read_sql(f"SELECT SUM(scope2_market_based_kg)/1000.0 as ton FROM f_Energi", conn).iloc[0,0] or 0.0
        s3 = pd.read_sql(f"SELECT SUM(co2e_tonnes) as ton FROM f_Scope3_Calculations", conn).iloc[0,0] or 0.0
    except:
        s1, s2, s3 = 0.0, 0.0, 0.0
    
    # 2. SOCIAL DATA (S1)
    try:
        hr = pd.read_sql(f"SELECT * FROM f_HR_Arsdata WHERE ar = {year}", conn).iloc[0]
    except:
        hr = {}

    # 3. GOVERNANCE (G1)
    try:
        policies = pd.read_sql("SELECT * FROM f_Governance_Policies", conn)
    except:
        policies = pd.DataFrame()

    # 4. DMA (Väsentlighet)
    try:
        dma = pd.read_sql("SELECT * FROM f_DMA_Materiality WHERE is_material = 1", conn)
    except:
        dma = pd.DataFrame()

    # Formatera strängar
    dma_str = "\n".join([f"- **{row['topic']}** ({row['category']})" for _, row in dma.iterrows()]) if not dma.empty else "_Inga väsentliga ämnen identifierade._"
    pol_str = "\n".join([f"- {row['policy_name']} (Version: {row['document_version']})" for _, row in policies.iterrows()]) if not policies.empty else "_Inga policyer registrerade._"

    kvinnor = hr.get('ledning_kvinnor', 0)
    man = hr.get('ledning_man', 0)
    total = kvinnor + man
    pct = (kvinnor / total * 100) if total > 0 else 0

    report_md = f"""
# Hållbarhetsrapport {year}
**Företaget AB**

## ESRS 2: Allmänna upplysningar
### Väsentliga hållbarhetsfrågor (DMA)
{dma_str}

---

## ESRS E1: Klimatpåverkan
- **Scope 1:** {s1:.2f} ton CO2e
- **Scope 2:** {s2:.2f} ton CO2e
- **Scope 3:** {s3:.2f} ton CO2e
**Totalt:** {s1+s2+s3:.2f} ton CO2e

---

## ESRS S1: Egen personal
- **Könsfördelning i ledning:** {kvinnor} kvinnor, {man} män ({pct:.1f}% kvinnor)
- **eNPS:** {hr.get('enps_intern', 'N/A')}

---

## ESRS G1: Affärsetik
### Aktiva Policyer
{pol_str}

---
*Rapporten genererad {datetime.now().strftime('%Y-%m-%d %H:%M')} via ESG Tool.*
"""

    html_content = markdown.markdown(report_md)
    # Add some basic styling
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', sans-serif; color: #333; line-height: 1.6; padding: 40px; }}
            h1 {{ color: #2962FF; border-bottom: 2px solid #2962FF; padding-bottom: 10px; }}
            h2 {{ color: #00E5FF; margin-top: 30px; }}
            hr {{ border: 0; border-top: 1px solid #eee; margin: 20px 0; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    pdf_path = f"ESG_Report_{year}.pdf"
    
    if HTML:
        try:
            HTML(string=styled_html).write_pdf(pdf_path)
        except Exception as e:
            # Fallback to text file if PDF conversion fails
            with open(pdf_path, "w", encoding="utf-8") as f:
                f.write(report_md)
    else:
        # Fallback to text file
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(report_md)
            
    return pdf_path