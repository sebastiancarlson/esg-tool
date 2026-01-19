import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import plotly.express as px
from datetime import datetime

# Import local modules
try:
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel

# ============================================
# 1. CONFIG & AUTH
# ============================================
st.set_page_config(page_title="ESG Hållbarhetsindex", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

if st.query_params.get("logout") == "1":
    st.session_state["password_correct"] = False
    st.query_params.clear()
    st.rerun()

def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "AdminESG2026!":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""<style>.stApp {background-color: #0A0E17; background-image: radial-gradient(circle at 50% 0%, #1a2642 0%, #0A0E17 70%);} .auth-container {max-width: 400px; margin: 100px auto; padding: 40px; background: rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); text-align: center;} h1 { color: white; margin-bottom: 30px; font-weight: 300; }</style>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("<h1>ESG <span style='color:#00E5FF; font-weight:800;'>Admin</span></h1>", unsafe_allow_html=True)
            st.text_input("Användarnamn", key="username")
            st.text_input("Lösenord", type="password", key="password")
            if st.button("Logga in", type="primary", use_container_width=True):
                password_entered()
                st.rerun()
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Fel användarnamn eller lösenord")
        return False
    return True

if not check_password():
    st.stop()

# ============================================
# 2. THEME & STYLING (SAFE MODE)
# ============================================
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = True

theme = {
    'bg': '#0A0E17' if st.session_state['dark_mode'] else '#F2F4F8',
    'bg_gradient': 'radial-gradient(circle at 50% 0%, #1a2642 0%, #0A0E17 70%)' if st.session_state['dark_mode'] else 'linear-gradient(180deg, #F2F4F8 0%, #E2E8F0 100%)',
    'card_bg': 'rgba(21, 27, 43, 0.6)' if st.session_state['dark_mode'] else '#FFFFFF',
    'card_border': 'rgba(255, 255, 255, 0.08)' if st.session_state['dark_mode'] else 'rgba(0, 0, 0, 0.05)',
    'text_main': '#F0F2F6' if st.session_state['dark_mode'] else '#171717',
    'text_muted': '#B0B8C6' if st.session_state['dark_mode'] else '#64748B',
    'sidebar_bg': '#0d1117' if st.session_state['dark_mode'] else '#FFFFFF',
    'shadow': '0 4px 20px rgba(0, 0, 0, 0.3)' if st.session_state['dark_mode'] else '0 2px 15px rgba(0, 0, 0, 0.05)',
    'input_bg': 'rgba(255,255,255,0.05)' if st.session_state['dark_mode'] else '#F8FAFC'
}

css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    :root {
        --esg-blue-primary: #2962FF;  
        --esg-cyan: #00E5FF;          
        --bg-dark: VAR_BG;
        --bg-card: VAR_CARD_BG;             
        --text-main: VAR_TEXT_MAIN;
        --text-muted: VAR_TEXT_MUTED;
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-main) !important;
        background-color: var(--bg-dark) !important;
    }
    
    .stApp {
        background-color: var(--bg-dark);
        background-image: VAR_GRADIENT;
        background-attachment: fixed;
    }

    [data-testid="stSidebar"] {
        background-color: VAR_SIDEBAR_BG !important;
        border-right: 1px solid VAR_CARD_BORDER;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text-main) !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {
        color: var(--text-main) !important;
    }

    [data-testid="stSidebar"] div.stButton {
        margin-bottom: -15px !important;
    }

    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        border: none;
        background-color: transparent;
        color: var(--text-muted);
        padding: 12px 20px !important;
        font-size: 16px;
        transition: all 0.3s ease;
        border-radius: 8px;
        margin-bottom: 5px;
        align-items: center;
    }

    [data-testid="stSidebar"] div.stButton > button > div {
        justify-content: flex-start !important;
        text-align: left !important;
    }

    div.stButton > button:hover {
        background-color: rgba(125, 125, 125, 0.1);
        color: var(--text-main);
        transform: translateX(5px);
    }
    
    div.stButton > button:focus {
        border: none;
        outline: none;
        color: var(--text-main);
    }

    /* Active button highlight */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: rgba(0, 229, 255, 0.15) !important;
        color: #00E5FF !important;
        border-left: 4px solid #00E5FF !important;
        border-radius: 4px 12px 12px 4px !important;
    }

    .css-card {
        background-color: var(--bg-card);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid VAR_CARD_BORDER;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: VAR_SHADOW;
    }
    
    .css-card h3 {
        color: var(--text-main) !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div, .stDateInput div {
        background-color: VAR_INPUT_BG !important;
        color: var(--text-main) !important;
        border-color: VAR_CARD_BORDER !important;
    }

    .gradient-text {
        background: linear-gradient(90deg, var(--text-main) 0%, #00E5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
"""

css = css.replace("VAR_BG", theme['bg'])
css = css.replace("VAR_CARD_BG", theme['card_bg'])
css = css.replace("VAR_TEXT_MAIN", theme['text_main'])
css = css.replace("VAR_TEXT_MUTED", theme['text_muted'])
css = css.replace("VAR_GRADIENT", theme['bg_gradient'])
css = css.replace("VAR_SIDEBAR_BG", theme['sidebar_bg'])
css = css.replace("VAR_CARD_BORDER", theme['card_border'])
css = css.replace("VAR_SHADOW", theme['shadow'])
css = css.replace("VAR_INPUT_BG", theme['input_bg'])

st.markdown(css, unsafe_allow_html=True)

# ============================================
# 3. DATABASE & HELPERS
# ============================================
DB_PATH = os.path.join("database", "esg_index.db")
if not os.path.exists(DB_PATH) and os.path.exists(os.path.join("..", DB_PATH)): DB_PATH = os.path.join("..", DB_PATH)

def get_connection(): return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        # Table list
        tables = [
            "CREATE TABLE IF NOT EXISTS f_HR_Arsdata (ar INTEGER PRIMARY KEY, enps_intern INTEGER, cnps_konsult INTEGER, antal_interna INTEGER, antal_konsulter INTEGER, nyanstallda_ar INTEGER, sjukfranvaro_procent REAL, arbetsolyckor_antal INTEGER, allvarliga_olyckor INTEGER DEFAULT 0, ledning_kvinnor INTEGER DEFAULT 0, ledning_man INTEGER DEFAULT 0, inspirerade_barn_antal INTEGER DEFAULT 0, utbildning_timmar_snitt REAL DEFAULT 0, employee_category TEXT, gender_pay_gap_pct REAL)",
            "CREATE TABLE IF NOT EXISTS f_Pendling_Beraknad (berakning_id INTEGER PRIMARY KEY AUTOINCREMENT, uppdrag_id INTEGER, antal_arbetsdagar REAL, total_km REAL, emissionsfaktor_kg_per_km REAL, totalt_co2_kg REAL, datakvalitet TEXT)",
            "CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT, description TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Vasentlighet (id INTEGER PRIMARY KEY AUTOINCREMENT, omrade TEXT, impact_score INTEGER, fin_score INTEGER, ar INTEGER)",
            "CREATE TABLE IF NOT EXISTS f_Governance_Inkop (ar INTEGER PRIMARY KEY, uppforandekod_pct INTEGER, visselblasare_antal INTEGER, gdpr_incidenter INTEGER, it_inkop_co2 REAL, lev_krav_pct INTEGER)",
            "CREATE TABLE IF NOT EXISTS f_DMA_Materiality (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL, impact_score INTEGER, financial_score INTEGER, esrs_code TEXT, category TEXT, stakeholder_input TEXT, created_date TEXT, last_updated TEXT, is_material INTEGER DEFAULT 0)",
            "CREATE TABLE IF NOT EXISTS f_Scope3_Calculations (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, subcategory TEXT, product_name TEXT, spend_sek REAL, emission_factor REAL, co2e_tonnes REAL, data_quality TEXT, reporting_period TEXT, source_document TEXT, created_date TEXT)", 
            "CREATE TABLE IF NOT EXISTS f_Governance_Policies (id INTEGER PRIMARY KEY AUTOINCREMENT, policy_name TEXT UNIQUE, document_version TEXT, owner TEXT, last_updated DATE, next_review_date DATE, is_implemented INTEGER DEFAULT 0, document_link TEXT, esrs_requirement TEXT, notes TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Social_Metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, metric_type TEXT, value REAL, period TEXT, data_source TEXT, employee_category TEXT)",
            "CREATE TABLE IF NOT EXISTS f_ESRS_Requirements (esrs_code TEXT PRIMARY KEY, disclosure_requirement TEXT, description TEXT, mandatory INTEGER DEFAULT 1, applies_to_company INTEGER DEFAULT 1)",
            "CREATE TABLE IF NOT EXISTS f_Drivmedel (id INTEGER PRIMARY KEY AUTOINCREMENT, datum TEXT, volym_liter REAL, drivmedelstyp TEXT, co2_kg REAL, kvitto_ref TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Energi (id INTEGER PRIMARY KEY AUTOINCREMENT, ar INTEGER, manad INTEGER, anlaggning_id TEXT, el_kwh REAL, fjarrvarme_kwh REAL, el_kalla TEXT, scope2_location_based_kg REAL, scope2_market_based_kg REAL)",
            "CREATE TABLE IF NOT EXISTS d_Personal (person_id INTEGER PRIMARY KEY AUTOINCREMENT, fornamn TEXT, efternamn TEXT, hem_postnummer TEXT)",
            "CREATE TABLE IF NOT EXISTS d_Kundsiter (kund_plats_id INTEGER PRIMARY KEY AUTOINCREMENT, kund_namn TEXT, postnummer TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Uppdrag (uppdrag_id INTEGER PRIMARY KEY AUTOINCREMENT, person_id INTEGER, kund_plats_id INTEGER, startdatum TEXT, slutdatum TEXT, dagar_per_vecka REAL, distans_km REAL, fardmedel TEXT)",
            "CREATE TABLE IF NOT EXISTS d_Kontor (kontor_id INTEGER PRIMARY KEY AUTOINCREMENT, namn TEXT, aktiv INTEGER DEFAULT 1)",
            "CREATE TABLE IF NOT EXISTS f_Riskregister (risk_id INTEGER PRIMARY KEY AUTOINCREMENT, beskrivning TEXT, status TEXT DEFAULT 'Öppen')"
        ]
        for sql in tables: conn.execute(sql)
        try: conn.execute("INSERT INTO system_config (key, value, description) VALUES ('company_name', 'Företaget AB', 'Företagsnamn')")
        except: pass
        try: 
            conn.execute("ALTER TABLE f_Scope3_Calculations ADD COLUMN product_name TEXT")
        except: pass
        try: 
            if conn.execute("SELECT COUNT(*) FROM f_ESRS_Requirements").fetchone()[0] == 0:
                conn.executemany("INSERT INTO f_ESRS_Requirements VALUES (?, ?, ?, 1, 1)", [("E1-6", "GHG emissions", "Klimat", 1), ("S1-1", "Policies", "Personal", 1)])
        except: pass

init_db()

def show_page_help(text):
    with st.expander("📘 Guide: Så fungerar denna vy", expanded=False):
        st.markdown(text)

if 'page' not in st.session_state: st.session_state.page = "Översikt"

# ============================================
# 4. PAGE FRAGMENTS
# ============================================

@st.fragment
def render_overview(conn):
    st.markdown('<h1 style="font-size: 3rem;">ESG <span class="gradient-text">Evidence Engine</span></h1>', unsafe_allow_html=True)
    st.markdown("Centraliserad plattform för hållbarhetsdata, rapportering och analys.", unsafe_allow_html=True)
    
    show_page_help("""
    ### 👋 Välkommen till ESG Evidence Engine
    
    Denna instrumentpanel ger dig en realtidsbild av bolagets hållbarhetsprestanda och efterlevnad av EU-direktivet CSRD.
    
    #### 📊 KPI-Förklaring
    *   **CO2 Scope 1:** Direkta utsläpp från källor ni äger (t.ex. tjänstebilar).
    *   **CO2 Scope 2:** Indirekta utsläpp från inköpt energi (el, fjärrvärme).
    *   **CO2 Scope 3:** Utsläpp i värdekedjan (pendling, inköp, tjänster). Ofta 80-90% av totalen.
    *   **CSRD Readiness:** Ett beräknat betyg (0-100%) på hur många av de obligatoriska datapunkterna i ESRS som är ifyllda i systemet.
    
    #### 🎯 Syfte
    Att snabbt identifiera dataluckor och följa trenden mot Net Zero och Compliance.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CO2 Scope 1", "12.5 ton", "-2%")
    col2.metric("CO2 Scope 2", "4.2 ton", "-15%")
    col3.metric("CO2 Scope 3", "Calculating...", "Pending")
    try:
        idx_data = index_generator.get_esrs_index(2024) 
        score = index_generator.calculate_readiness_score(idx_data)
        col4.metric("CSRD Readiness", f"{score}%", "+5%")
    except: col4.metric("CSRD Readiness", "0%", "N/A")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Systemstatus")
    st.progress(85, text="Datakvalitet Scope 1 & 2")
    st.progress(40, text="Datakvalitet Scope 3 (Pendling)")
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_strategy(conn):
    st.title("Strategi & Väsentlighet")
    
    show_page_help("""
    ### 🧭 Dubbel Väsentlighetsanalys (DMA)
    
    Enligt CSRD (ESRS 2) räcker det inte att bara rapportera det man "känner för". Man måste vetenskapligt bedöma vad som är väsentligt.
    
    #### 🛠 Gör så här:
    1.  **Ämne:** Ange ett hållbarhetsområde (t.ex. "Klimat", "Arbetsmiljö", "Anti-korruption").
    2.  **Impact (Påverkan):** Bedöm er påverkan på människa/miljö. (1=Försumbar, 5=Allvarlig/Irreversibel).
    3.  **Finansiell Risk:** Bedöm risken för bolagets ekonomi. (1=Försumbar, 5=Hotar affärsmodellen).
    
    #### 📈 Resultat & Mätning
    Systemet skapar en matris. Ämnen med **poäng ≥ 3** på *någon* axel klassas som **Väsentliga**. Dessa hamnar automatiskt i ESRS-indexet och *måste* rapporteras.
    """)
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Dubbel Väsentlighetsanalys (DMA)")
    dma_data = dma_tool.get_dma_data() 
    if not dma_data.empty:
        fig = px.scatter(dma_data, x="financial_score", y="impact_score", text="topic", color="category", size_max=20, range_x=[0.5, 5.5], range_y=[0.5, 5.5])
        fig.add_hline(y=2.5, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig.add_vline(x=2.5, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white" if st.session_state['dark_mode'] else "black", height=500)
        st.plotly_chart(fig, use_container_width=True)
    with st.form("dma_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Ämne")
            cat = st.selectbox("Kategori", ["Miljö (E)", "Socialt (S)", "Styrning (G)"])
        with col2:
            imp = st.slider("Impact", 1, 5, 3)
            fin = st.slider("Finansiell", 1, 5, 3)
        if st.form_submit_button("Lägg till"):
            dma_tool.add_dma_topic(conn, topic, imp, fin, cat)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_hr(conn):
    st.title("HR & Social Hållbarhet")
    
    show_page_help("""
    ### 👥 Social Hållbarhet (S1 & S2)
    
    CSRD kräver att vi skiljer på personer vi har direkt juridiskt ansvar för och de som arbetar i vår värdekedja.
    
    #### 1. S1: Egen Personal (Own Workforce)
    *   **Vem:** Personer med anställningsavtal och löneutbetalning från er.
    *   **Mätetal:** Sjukfrånvaro (%), Olycksfall (antal), Utbildning (timmar/år) och Gender Pay Gap (okorrigerat).
    *   **Syfte:** Säkerställa en trygg och jämställd arbetsplats.
    
    #### 2. S2: Arbetstagare i värdekedjan (Workers in Value Chain)
    *   **Vem:** Konsulter, underkonsulter och gig-arbetare.
    *   **Mätetal:** Antal (FTE), Arbetsmiljöincidenter hos kund.
    *   **Syfte:** Ta ansvar även för de som bidrar till värdeskapandet utan att vara anställda.
    """)
    
    tab_s1, tab_s2, tab_hist = st.tabs(["👥 S1: Egen Personal", "🚜 S2: Konsulter", "📈 Historik"])
    with tab_s1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        with st.form("s1_form"):
            ar = st.number_input("År", 2024)
            c1, c2 = st.columns(2)
            with c1:
                interna = st.number_input("Antal interna", min_value=0)
                pay_gap = st.number_input("Gender Pay Gap %", 0.0)
            with c2:
                utb = st.number_input("Utbildningstimmar", 0.0)
                enps = st.slider("eNPS", -100, 100, 10)
            if st.form_submit_button("Spara S1"):
                data = {'ar': ar, 'enps_intern': enps, 'cnps_token': 0, 'antal_interna': interna, 'antal_konsulter': 0, 'nyanstallda_ar': 0, 'sjukfranvaro_procent': 0, 'arbetsolyckor_antal': 0, 'inspirerade_barn_antal': 0, 'utbildning_timmar_snitt': utb, 'employee_category': 'Internal', 'gender_pay_gap_pct': pay_gap}
                social_tracker.save_extended_hr_data(conn, data)
                st.success("Sparat!")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_s2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        # Using summary without conn in future if cached, but for now passing conn to save
        with st.form("s2_form"):
            ar = st.number_input("År", 2024, key="s2_ar")
            konsulter = st.number_input("Antal konsulter", 0)
            if st.form_submit_button("Spara S2"):
                st.success("Sparat!")
        st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_governance(conn):
    st.title("Governance & Leverantörskedja")
    
    show_page_help("""
    ### ⚖️ Styrning & Kontroll (G1)
    
    Governance handlar om "ordning och reda". För att vara compliant måste styrdokument vara uppdaterade och implementerade.
    
    #### 📚 Policy-bibliotek
    *   **Funktion:** Ladda upp namn och datum för styrdokument (t.ex. Uppförandekod, Visselblåsarpolicy).
    *   **Logik:** Systemet räknar automatiskt ut **Nästa Översyn** (1 år från fastställande).
    *   **Varningar:** 
        *   🟢 Grön: Giltig.
        *   🟡 Gul: Dags att se över (<90 dagar kvar).
        *   🔴 Röd: Utgången (Risk för non-compliance).
    """)
    
    tab_pol, tab_kpi = st.tabs(["📚 Policys", "📊 KPI"])
    with tab_pol:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        pols = governance.get_policies() # REMOVED CONN
        if not pols.empty: st.dataframe(pols[['Status', 'policy_name', 'next_review_date']], hide_index=True, use_container_width=True)
        with st.form("add_pol"):
            name = st.text_input("Dokumentnamn")
            owner = st.text_input("Ägare")
            date = st.date_input("Fastställd")
            if st.form_submit_button("Spara"):
                governance.add_policy(conn, name, "1.0", owner, date, "G1")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_calc(conn):
    st.title("Automatiska Beräkningar")
    
    show_page_help("""
    ### 🧮 Klimatberäkningar (Scope 3)
    
    Att mäta värdekedjans utsläpp är komplext. Vi använder två metoder:
    
    #### 1. Spend-analys (Inköp)
    *   **När:** För varor och tjänster där vi saknar exakt data (t.ex. IT-konsulter, kontorsmaterial).
    *   **Hur:** Vi multiplicerar kostnaden (SEK) med en **Emissionsfaktor** (kg CO2e/SEK) baserad på branschsnitt (SCB/Exiobase).
    *   **Exempel:** 100 000 kr på IT-hårdvara -> ca 4.5 ton CO2e.
    
    #### 2. Aktivitetsdata (Pendling)
    *   **När:** När vi vet fysiska avstånd.
    *   **Hur:** (Distans km × 2) × Arbetsdagar × Fordonets utsläppsfaktor.
    *   **Resultat:** Ett mer precist värde än spend-analys.
    """)
    
    t1, t2, t3, t4 = st.tabs(["Pendling", "Inköp (Spend)", "🔍 Detaljanalys", "Uppdatera"])
    with t2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1,2])
        with c1:
            with st.form("spend"):
                cat = st.selectbox("Kategori", scope3_spend.get_categories())
                sub = st.text_input("Underkategori", placeholder="T.ex. Fruktkorg")
                prod = st.text_input("Produkt/Leverantör", placeholder="T.ex. Mathem") 
                sek = st.number_input("SEK", 0.0)
                ar = st.selectbox("År", ["2024", "2025"], key="spend_year")
                if st.form_submit_button("Lägg till"):
                    scope3_spend.add_spend_item(conn, cat, sub, prod, sek, ar) 
                    st.success("Sparat!")
        with c2:
            summ = scope3_spend.get_spend_summary(ar) # REMOVED CONN
            if not summ.empty: st.dataframe(summ, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t3: # Detail Analysis
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Djupdykning: Produkter & Leverantörer")
        ar_det = st.selectbox("Välj år", ["2024", "2025"], key="det_year")
        
        details = scope3_spend.get_product_breakdown(ar_det) 
        
        if not details.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Topp 5 Utsläppskällor")
                fig = px.pie(details.head(10), values='co2', names='product_name', title='Fördelning per Produkt', hole=0.4)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white" if st.session_state['dark_mode'] else "black")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown("##### Detaljerad Lista")
                st.dataframe(details, hide_index=True, use_container_width=True)
        else:
            st.info("Ingen produktspecifik data inmatad än.")
        st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_reports(conn):
    st.title("Generera Rapporter")
    
    show_page_help("""
    ### 📑 Export & Rapportering
    
    Här tar du ut datan för extern granskning.
    
    #### 1. CSRD-rapport (PDF)
    *   **Vad:** En textrapport strukturerad enligt ESRS E1, S1 och G1.
    *   **Innehåll:** Automatiskt genererad text baserad på era KPI:er och DMA-analys.
    *   **Användning:** Underlag för årsredovisning eller hållbarhetsrapport.
    
    #### 2. ESRS Index
    *   **Vad:** En tabell som mappar varje krav (t.ex. E1-6) mot er data.
    *   **Användning:** "Fusklapp" för revisorn för att snabbt se om ni uppfyller kraven (Gap-analys).
    """)
    
    t1, t2 = st.tabs(["CSRD", "Index"])
    with t1:
        if st.button("Ladda ner PDF"):
            path = report_csrd.generate_csrd_report(conn, 2024)
            with open(path, "rb") as f: st.download_button("Download", f, file_name="report.pdf")

@st.fragment
def render_audit(conn):
    st.title("Audit Trail")
    show_page_help("""
    **Endast för granskning.** Här kan en revisor dyka ner i enskilda datapunkter (t.ex. en specifik pendlingsberäkning) för att verifiera källan och beräkningsmetoden.
    """)
    st.info("Här visas transaktionsloggar.")

@st.fragment
def render_settings(conn):
    st.title("Inställningar")
    
    show_page_help("""
    Konfigurera systemet för er organisation.
    
    *   **Företagsinfo:** Namn och grunddata.
    *   **Import:** Ladda upp Excel-filer för att slippa manuell inmatning.
    *   **Backup:** Ladda ner en kopia av hela databasen (rekommenderas före stora ändringar).
    """)
    
    t1, t2, t3, t4 = st.tabs(["Info", "Import", "Datahantering", "Vy & Tema"])
    
    with t4:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Tema")
        is_dark = st.toggle("Mörkt läge", value=st.session_state['dark_mode'])
        if is_dark != st.session_state['dark_mode']:
            st.session_state['dark_mode'] = is_dark
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        try:
            config = pd.read_sql("SELECT * FROM system_config", conn)
            for _, row in config.iterrows():
                st.text_input(row['description'], value=row['value'], key=row['key'], disabled=True)
            st.caption("Kontakta admin för att ändra systemparametrar.")
        except: st.info("Ingen konfiguration hittades.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Importera från Excel")
        uploaded = st.file_uploader("Ladda upp HR-export", type=['xlsx', 'csv'])
        if uploaded: st.info("Importfunktionen är inaktiverad i demoläge.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t3:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("💾 Datahantering (Snapshot)")
        st.info("Systemet nollställs vid omstart. Spara din data här för att kunna fortsätta senare.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 1. Spara arbete")
            try:
                with open(DB_PATH, "rb") as f:
                    st.download_button(
                        label="Ladda ner Systemfil (.db)",
                        data=f,
                        file_name=f"ESG_Data_{datetime.now().strftime('%Y-%m-%d')}.db",
                        mime="application/octet-stream",
                        type="primary"
                    )
            except: st.error("Kunde inte läsa databasen.")
            
        with c2:
            st.markdown("#### 2. Återställ arbete")
            uploaded_db = st.file_uploader("Släpp din .db fil här", type="db")
            if uploaded_db:
                if st.button("⚠️ Ersätt & Ladda om", type="secondary"):
                    with open(DB_PATH, "wb") as f:
                        f.write(uploaded_db.getbuffer())
                    st.success("Återställd! Startar om...")
                    time.sleep(1)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================ 
# 5. SIDEBAR & ROUTING
# ============================================ 
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 10px 0 25px 0;'><h1 style='margin: 0; font-weight: 800; letter-spacing: 4px; color: VAR_TEXT; font-size: 2.5rem;'>ESG</h1><div style='height: 2px; background: linear-gradient(90deg, transparent, #00E5FF, transparent); margin: 5px auto; width: 80%;'></div><p style='margin: 0; color: #00E5FF; font-family: Inter, sans-serif; font-weight: 300; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase;'>Hållbarhetsindex</p></div>".replace("VAR_TEXT", theme['text_main']), unsafe_allow_html=True)
    st.markdown("---")
    nav_items = {"Översikt": ":material/dashboard:", "Strategi (CSRD)": ":material/target:", "HR-Data": ":material/groups:", "Governance": ":material/gavel:", "Beräkningar": ":material/calculate:", "Rapporter": ":material/article:", "Revisorvy": ":material/find_in_page:", "Inställningar": ":material/settings:"}
    for label, icon in nav_items.items():
        if st.button(label, icon=icon, key=label, type="primary" if st.session_state.page == label else "secondary", use_container_width=True):
            st.session_state.page = label
            st.rerun()
    st.markdown("---")
    card_bg = "rgba(255, 255, 255, 0.03)" if st.session_state['dark_mode'] else "rgba(0, 0, 0, 0.03)"
    border_col = "rgba(255, 255, 255, 0.05)" if st.session_state['dark_mode'] else "rgba(0, 0, 0, 0.05)"
    text_col = "#FFFFFF" if st.session_state['dark_mode'] else "#171717"
    st.markdown(f"<div style='background-color: {card_bg}; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid {border_col}; display: flex; align-items: center; justify-content: space-between;'><div style='display: flex; align-items: center;'><div style='width: 34px; height: 34px; background: linear-gradient(135deg, #00E5FF 0%, #2962FF 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 10px; font-size: 14px;'>J</div><div><div style='color: {text_col}; font-weight: 600; font-size: 13px;'>Jenny</div><div style='color: {theme['text_muted']}; font-size: 10px;'>System Admin</div></div></div><a href='?logout=1' target='_self' style='color: {theme['text_muted']}; text-decoration: none; padding: 5px;'><span style='font-size: 18px;'>⏻</span></a></div>", unsafe_allow_html=True)

conn = get_connection()
if st.session_state.page == "Översikt": render_overview(conn)
elif st.session_state.page == "Strategi (CSRD)": render_strategy(conn)
elif st.session_state.page == "HR-Data": render_hr(conn)
elif st.session_state.page == "Governance": render_governance(conn)
elif st.session_state.page == "Beräkningar": render_calc(conn)
elif st.session_state.page == "Rapporter": render_reports(conn)
elif st.session_state.page == "Revisorvy": render_audit(conn)
elif st.session_state.page == "Inställningar": render_settings(conn)
conn.close()
