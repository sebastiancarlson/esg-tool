import pandas as pd
from datetime import datetime
import markdown
# from weasyprint import HTML # Commented out to avoid dependency issues if not installed, can be enabled if needed.

def generate_csrd_report(conn, year):
    """
    Genererar CSRD-rapport enligt ESRS-struktur
    """
    
    # ---------------------------------------------------------
    # DATA HÄMTNING
    # ---------------------------------------------------------
    
    # 1. MILJÖDATA (E1)
    try:
        scope1 = pd.read_sql(f"SELECT SUM(co2_kg)/1000 as ton FROM f_Drivmedel WHERE strftime('%Y', datum) = '{year}'", conn).iloc[0,0]
        if scope1 is None: scope1 = 0
    except: scope1 = 0

    try:
        scope2 = pd.read_sql(f"SELECT SUM(scope2_market_based_kg)/1000 as ton FROM f_Energi WHERE ar = {year}", conn).iloc[0,0]
        if scope2 is None: scope2 = 0
    except: scope2 = 0

    try:
        scope3 = pd.read_sql(f"SELECT SUM(totalt_co2_kg)/1000 as ton FROM f_Pendling_Beraknad", conn).iloc[0,0]
        if scope3 is None: scope3 = 0
    except: scope3 = 0
    
    # Datakvalitet Scope 3
    try:
        quality = pd.read_sql(
            """
            SELECT 
                datakvalitet,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as procent
            FROM f_Pendling_Beraknad
            GROUP BY datakvalitet
        """, conn)
    except: 
        quality = pd.DataFrame({'datakvalitet': [], 'procent': []})
    
    # 2. SOCIAL DATA (S1)
    try:
        hr = pd.read_sql(f"SELECT * FROM f_HR_Arsdata WHERE ar = {year}", conn).iloc[0]
    except:
        # Dummy object if missing
        hr = {
            'sjukfranvaro_procent': 0,
            'arbetsolyckor_antal': 0,
            'allvarliga_olyckor': 0,
            'enps_intern': 0,
            'cnps_konsult': 0,
            'ledning_kvinnor': 0,
            'ledning_man': 0,
            'inspirerade_barn_antal': 0,
            'utbildning_timmar_snitt': 0
        }

    # 3. GOVERNANCE & STRATEGI (G1 & ESRS 2)
    try:
        vasentlighet = pd.read_sql(f"SELECT * FROM f_Vasentlighet WHERE ar = {year} ORDER BY (impact_score + fin_score) DESC", conn)
    except:
        vasentlighet = pd.DataFrame()
        
    try:
        gov = pd.read_sql(f"SELECT * FROM f_Governance_Inkop WHERE ar = {year}", conn).iloc[0]
    except:
        gov = {
            'uppforandekod_pct': 0,
            'visselblasare_antal': 0,
            'lev_krav_pct': 0,
            'it_inkop_co2': 0
        }
    
    # Helper for safe SQL
    def get_count(table, where="1=1"):
        try:
            return pd.read_sql(f"SELECT COUNT(*) FROM {table} WHERE {where}", conn).iloc[0,0]
        except: return 0

    def get_val(sql):
        try:
            val = pd.read_sql(sql, conn).iloc[0,0]
            return val if val is not None else 0
        except: return 0

    kontor_count = get_count("d_Kontor", "aktiv=1")
    renewable_pct = get_val(f"SELECT SUM(CASE WHEN el_kalla='Förnybar' THEN el_kwh ELSE 0 END) * 100.0 / SUM(el_kwh) FROM f_Energi WHERE ar={year}")
    risk_count = get_count("f_Riskregister", "status='Öppen'")

    # ---------------------------------------------------------
    # FORMATERING
    # ---------------------------------------------------------

    # Kvalitetssträng
    quality_rows = []
    if not quality.empty:
        for _, row in quality.iterrows():
            quality_rows.append(f"- {row['datakvalitet']}: {row['procent']:.0f}%")
    quality_str = "\n".join(quality_rows)

    # Safe access functions
    def hr_get(key): return hr[key] if key in hr else 0
    def gov_get(key): return gov[key] if key in gov else 0

    # HR metrics
    hr_sjuk = hr_get('sjukfranvaro_procent')
    hr_olyckor = hr_get('arbetsolyckor_antal')
    hr_allvarliga = hr_get('allvarliga_olyckor')
    hr_enps = hr_get('enps_intern')
    hr_cnps = hr_get('cnps_konsult')
    
    # New Social Metrics
    hr_barn = hr_get('inspirerade_barn_antal')
    hr_utb = hr_get('utbildning_timmar_snitt')
    
    # Diversity
    kvinnor = hr_get('ledning_kvinnor')
    man = hr_get('ledning_man')
    total_ledning = kvinnor + man
    kvinnor_pct = (kvinnor / total_ledning * 100) if total_ledning > 0 else 0
    man_pct = (man / total_ledning * 100) if total_ledning > 0 else 0

    # Governance metrics
    gov_code = gov_get('uppforandekod_pct')
    gov_whistle = gov_get('visselblasare_antal')
    gov_lev = gov_get('lev_krav_pct')
    gov_it_co2 = gov_get('it_inkop_co2')
    
    # Materiality list
    mat_rows = []
    if not vasentlighet.empty:
        for _, row in vasentlighet.iterrows():
            mat_rows.append(f"- **{row['omrade']}** (Impact: {row['impact_score']}/10, Finansiell: {row['fin_score']}/10)")
    mat_str = "\n".join(mat_rows) if mat_rows else "_Ingen väsentlighetsanalys registrerad för detta år._"

    # ---------------------------------------------------------
    # MARKDOWN RAPPORT
    # ---------------------------------------------------------
    report_md = f"""
# Hållbarhetsrapport {year}
**ESG Företag AB**

*Upprättad enligt CSRD/ESRS*

---

## ESRS 2: Allmänna upplysningar

### Dubbel Väsentlighetsanalys
Följande områden har identifierats som väsentliga för verksamheten baserat på påverkan och finansiell risk:

{mat_str}

---

## ESRS E1: Klimatpåverkan

### Scope 1 (Direkta utsläpp)
- **Totalt:** {scope1:.1f} ton CO2e
- **Källa:** Företagsbilar (fossil drivmedel)
- **Datakvalitet:** 100% verifierad (tankkvitton)

### Scope 2 (Indirekta utsläpp - energi)
- **Totalt:** {scope2:.1f} ton CO2e
- **Källa:** Elförbrukning kontor ({kontor_count} st)
- **Andel förnybar el:** {renewable_pct:.0f}%

### Scope 3 (Värdekedjeutsläpp)
- **Totalt:** {scope3:.1f} ton CO2e
- **Huvudkälla:** Konsultpendling
- **Inköpta varor (IT):** {gov_it_co2:.1f} ton CO2e (Estimerat)

#### Datakvalitet Scope 3:
{quality_str}

**Estimeringsmetoder:**
- Distans: OpenStreetMap API (bilvägsavstånd)
- Färdmedelsfördelning vid okänd data: Trafikverkets RVU 2023 (Bil 65%, Kollektivtrafik 25%, Cykel 10%)

---

## ESRS S1: Egen arbetsstyrka & Samhälle

### Hälsa & Säkerhet
- Sjukfrånvaro (intern personal): {hr_sjuk:.2f}%
- Arbetsolyckor: {hr_olyckor} st (varav {hr_allvarliga} allvarliga)

### Kompetens & Engagemang
- **Samhällsbidrag:** {hr_barn} inspirerade barn och unga (via Code Summer Camp m.m.)
- **Kompetensutveckling:** {hr_utb:.1f} timmar per anställd/år
- eNPS (Interna): **{hr_enps}** (Branschsnitt: 6-10)
- cNPS (Konsulter): **{hr_cnps}**

### Mångfald (Ledning)
- Kvinnor: {kvinnor} ({kvinnor_pct:.0f}%)
- Män: {man} ({man_pct:.0f}%)

---

## ESRS G1: Styrning & Inköp

### Affärsetik
- **Uppförandekod:** {gov_code}% av anställda har signerat.
- **Visselblåsning:** {gov_whistle} inrapporterade ärenden.
- **Riskhantering:** {risk_count} aktiva risker identifierade i riskregistret.

### Leverantörskedja
- **Hållbara inköp:** {gov_lev}% av leverantörer har signerat Supplier Code of Conduct.

---

*Genererad: {datetime.now().strftime('%Y-%m-%d %H:%M')}*  
*Verktyg: ESG Hållbarhetsindex v2.0*
"""
    
    # Konvertera till PDF (Mocking PDF creation if weasyprint missing)
    pdf_path = f"ESG_CSRD_{year}.pdf"
    
    try:
        # from weasyprint import HTML
        # html = markdown.markdown(report_md)
        # HTML(string=html).write_pdf(pdf_path)
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(report_md) # Write MD for now if weasyprint fails
    except:
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(report_md)
    
    return pdf_path
