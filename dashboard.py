import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import plotly.express as px
from datetime import datetime
import importlib

# Import local modules
try:
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel
    from modules import scope3_travel 
    from modules import scope3_waste 
    from modules import scope3_purchased_goods 
    from modules import env_water
    from modules import env_waste
    
    # Force reload during development to catch updates
    importlib.reload(governance)
    importlib.reload(dma_tool)
    
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel
    from modules import scope3_travel 
    from modules import scope3_waste 
    from modules import scope3_purchased_goods 
    from modules import env_water
    from modules import env_waste 

# ============================================
# 1. CONFIG & AUTH
# ============================================
st.set_page_config(
    page_title="ESG Hållbarhetsindex", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        # Dark Login Screen
        st.markdown("<style>.stApp {background-color: #150B3F;}</style>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br><br><h1 style='color:#7CF7F9; text-align:center;'>ESG <span style='color:#FFFFFF;'>Workspace</span></h1>", unsafe_allow_html=True)
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
# 2. THEME & STYLING (SKILL BRAND IDENTITY)
# ============================================
st.markdown("""
<style>
    /* --- 1. FONTS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;800&display=swap');

    :root {
        /* BRAND COLORS - RGB DEFINITIONS */
        --skill-indigo: rgb(21, 11, 63);      /* Main Background */
        --skill-dark-indigo: rgb(15, 7, 45);  /* Card/Sidebar Background (Derived darker) */
        --skill-aqua: rgb(124, 247, 249);     /* Text / Accent */
        --skill-blue: rgb(26, 51, 245);       /* Primary Action */
        --skill-violet: rgb(111, 0, 255);     /* Secondary */
        --skill-lilac: rgb(243, 233, 255);    /* Light Backgrounds */
        --text-white: #FFFFFF;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--skill-aqua);
        background-color: var(--skill-indigo);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-white) !important;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    /* Paragraphs / Ingress */
    p, .skill-ingress {
        color: var(--skill-aqua);
        opacity: 0.9;
        font-weight: 300;
        line-height: 1.6;
    }
    
    /* --- 2. CARDS --- */
    .skill-card {
        background: var(--skill-dark-indigo);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(124, 247, 249, 0.05);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 24px;
    }
    
    .skill-card h3 {
        color: var(--skill-aqua) !important;
        opacity: 0.8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
    }
    
    .skill-card div {
        color: var(--text-white);
    }

    /* --- 3. BUTTONS (Badge-style / Subtle) --- */
    div.stButton > button {
        background-color: rgba(124, 247, 249, 0.05);
        color: var(--skill-aqua);
        border-radius: 8px;
        border: 1px solid rgba(124, 247, 249, 0.2);
        font-weight: 500;
        transition: all 0.2s ease;
        text-align: left;
        padding: 10px 15px;
    }
    
    div.stButton > button:hover {
        background-color: rgba(124, 247, 249, 0.15);
        border: 1px solid var(--skill-aqua);
        color: var(--skill-aqua);
        transform: translateY(-1px);
    }

    /* Active Page Button Highlight */
    div.stButton > button[kind="primary"] {
        background-color: rgba(124, 247, 249, 0.2);
        border: 1px solid var(--skill-aqua);
        color: #FFFFFF;
        font-weight: 700;
    }
    
    /* --- 4. SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: var(--skill-dark-indigo);
        border-right: 1px solid rgba(124, 247, 249, 0.05);
    }
    [data-testid="stSidebar"] h1 {
        color: var(--text-white);
    }
    
    /* --- 5. UI CLEANUP --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* --- 6. BACKGROUND BLOBS (Clean, Single Top-Right) --- */
    .stApp {
        background-image: url('data:image/svg+xml;utf8,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath fill="%237CF7F9" fill-opacity="0.05" d="M42.9,-69.5C52.9,-60.3,56.6,-43.9,59.5,-29.5C62.4,-15.2,64.4,-2.8,62.8,9.1C61.2,21.1,56,32.6,48.9,44.3C41.7,56,32.6,68,20,74.8C7.3,81.6,-8.8,83.2,-23.2,79C-37.7,74.8,-50.4,64.8,-56.4,52.1C-62.4,39.4,-61.6,24.1,-66,8.2C-70.3,-7.8,-79.8,-24.3,-76.8,-36.9C-73.9,-49.5,-58.5,-58.2,-43.6,-65.3C-28.7,-72.3,-14.3,-77.7,1,-79.3C16.4,-80.9,32.8,-78.7,42.9,-69.5Z" transform="translate(100 100)" /%3E%3C/svg%3E');
        background-repeat: no-repeat;
        background-position: right -10vw top -10vh;
        background-size: 70vw;
        background-attachment: fixed;
    }

</style>
""", unsafe_allow_html=True)

# ============================================
# 3. HELPERS
# ============================================

def skill_ingress(text):
    """Skriver ut en ingress (Inter 300)"""
    st.markdown(f'<p class="skill-ingress" style="font-size: 1.2rem; margin-top: 1rem;">{text}</p>', unsafe_allow_html=True)

def _render_badge_html(text, icon="leaf"):
    icons = {
        "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>',
        "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
        "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>',
        "file": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline>',
        "award": '<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>'
    }
    svg_icon = f'<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-{icon}" style="margin-right:6px; display:inline-block; vertical-align:text-bottom;">{icons.get(icon, icons["leaf"])}</svg>'
    
    return f"""
    <div style="
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 9999px;
        background-color: rgba(124, 247, 249, 0.08);
        border: 1px solid rgba(124, 247, 249, 0.2);
        color: #7CF7F9;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 8px;
        margin-top: 8px;
    ">
        {svg_icon}
        {text}
    </div>
    """

def skill_spotlight_header(title, subtitle=None, badges=None):
    """Skapar en header med Spotlight-grafik och inbakade badges"""
    
    badge_html = ""
    if badges:
        badge_html = "<div style='margin-top: 5px;'>" + "".join([_render_badge_html(b['text'], b.get('icon', 'leaf')) for b in badges]) + "</div>"

    st.html(f"""
    <div style="position:relative; padding: 20px 0 20px 0;">
        <h1 style="position:relative; z-index:1; margin-bottom:0; font-size: 3rem; color: #FFFFFF !important; line-height: 1.1;">{title}</h1>
        {f'<p style="font-weight:500; color:#7CF7F9; margin-top:5px; font-size: 1.1rem; text-transform:uppercase; letter-spacing:2px;">{subtitle}</p>' if subtitle else ''}
        {badge_html}
    </div>
    """)

def skill_card(title, value, delta=None):
    """Skapar ett kort enligt designsystemet (Dark Mode)"""
    delta_html = f'<span style="color:{"#00E5FF" if "+" in str(delta) else "#FF4B4B"}; font-size:0.9em; margin-left:10px;">{delta}</span>' if delta else ""
    st.markdown(f"""
    <div class="skill-card">
        <h3 style="margin:0;">{title}</h3>
        <div style="font-size:2.5rem; font-weight:800; margin-top:10px; color:#FFFFFF;">
            {value} {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_strategic_context(module_name):
    pass # Keeping clean

# ============================================
# 4. DB INIT
# ============================================
DB_PATH = os.path.join("database", "esg_index.db")
if not os.path.exists(DB_PATH) and os.path.exists(os.path.join("..", DB_PATH)): DB_PATH = os.path.join("..", DB_PATH)
def get_connection(): return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        tables = [
            "CREATE TABLE IF NOT EXISTS f_HR_Arsdata (ar INTEGER PRIMARY KEY, enps_intern INTEGER, cnps_konsult INTEGER, antal_interna INTEGER, antal_konsulter INTEGER, nyanstallda_ar INTEGER, sjukfranvaro_procent REAL, arbetsolyckor_antal INTEGER, allvarliga_olyckor INTEGER DEFAULT 0, ledning_kvinnor INTEGER DEFAULT 0, ledning_man INTEGER DEFAULT 0, inspirerade_barn_antal INTEGER DEFAULT 0, utbildning_timmar_snitt REAL DEFAULT 0, employee_category TEXT, gender_pay_gap_pct REAL)",
            "CREATE TABLE IF NOT EXISTS f_DMA_Materiality (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL, impact_score INTEGER, financial_score INTEGER, esrs_code TEXT, category TEXT, stakeholder_input TEXT, created_date TEXT, last_updated TEXT, is_material INTEGER DEFAULT 0)",
            "CREATE TABLE IF NOT EXISTS f_Scope3_Calculations (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, subcategory TEXT, product_name TEXT, spend_sek REAL, emission_factor REAL, co2e_tonnes REAL, data_quality TEXT, reporting_period TEXT, source_document TEXT, created_date TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Governance_Policies (id INTEGER PRIMARY KEY AUTOINCREMENT, policy_name TEXT UNIQUE, document_version TEXT, owner TEXT, last_updated DATE, next_review_date DATE, is_implemented INTEGER DEFAULT 0, document_link TEXT, esrs_requirement TEXT, notes TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Drivmedel (id INTEGER PRIMARY KEY AUTOINCREMENT, datum TEXT, volym_liter REAL, drivmedelstyp TEXT, co2_kg REAL, kvitto_ref TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Energi (id INTEGER PRIMARY KEY AUTOINCREMENT, ar INTEGER, manad INTEGER, anlaggning_id TEXT, el_kwh REAL, fjarrvarme_kwh REAL, el_kalla TEXT, scope2_location_based_kg REAL, scope2_market_based_kg REAL)",
            "CREATE TABLE IF NOT EXISTS d_Personal (person_id INTEGER PRIMARY KEY AUTOINCREMENT, fornamn TEXT, efternamn TEXT, hem_postnummer TEXT)",
            "CREATE TABLE IF NOT EXISTS d_Kundsiter (kund_plats_id INTEGER PRIMARY KEY AUTOINCREMENT, kund_namn TEXT, postnummer TEXT)",
            "CREATE TABLE IF NOT EXISTS f_Uppdrag (uppdrag_id INTEGER PRIMARY KEY AUTOINCREMENT, person_id INTEGER, kund_plats_id INTEGER, startdatum TEXT, slutdatum TEXT, dagar_per_vecka REAL, distans_km REAL, fardmedel TEXT)",
            "CREATE TABLE IF NOT EXISTS f_ESRS_Requirements (esrs_code TEXT PRIMARY KEY, disclosure_requirement TEXT, description TEXT, mandatory INTEGER DEFAULT 1, applies_to_company INTEGER DEFAULT 1)",
            "CREATE TABLE IF NOT EXISTS f_Scope3_BusinessTravel (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, travel_type TEXT, distance_km REAL, fuel_type TEXT, class_type TEXT, co2_kg REAL)",
            "CREATE TABLE IF NOT EXISTS f_Scope3_Waste (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, waste_type TEXT, weight_kg REAL, disposal_method TEXT, co2_kg REAL)",
            "CREATE TABLE IF NOT EXISTS f_Scope3_PurchasedGoodsServices (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount_sek REAL, emission_factor_kg_per_sek REAL, co2_kg REAL)",
            "CREATE TABLE IF NOT EXISTS f_Water_Data (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, site_id INTEGER, withdrawal_m3 REAL, withdrawal_source TEXT, discharge_m3 REAL, discharge_dest TEXT, consumption_m3 REAL, recycled_m3 REAL)",
            "CREATE TABLE IF NOT EXISTS f_Waste_Detailed (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, waste_category TEXT, is_hazardous INTEGER, weight_kg REAL, treatment_method TEXT, supplier TEXT)",
            "CREATE TABLE IF NOT EXISTS f_GAP_Analysis (esrs_code TEXT PRIMARY KEY, status TEXT, owner TEXT, evidence_link TEXT, notes TEXT, last_updated TEXT)",
            "CREATE TABLE IF NOT EXISTS f_DMA_IRO (id INTEGER PRIMARY KEY AUTOINCREMENT, dma_topic_id INTEGER, type TEXT, description TEXT, time_horizon TEXT, financial_effect TEXT)"
        ]
        for sql in tables: 
            try:
                conn.execute(sql)
            except sqlite3.Error as e:
                st.error(f"Database Init Error: {e}")
        
        # Populate ESRS Requirements if empty or update with fuller list
        try:
            count = conn.execute("SELECT COUNT(*) FROM f_ESRS_Requirements").fetchone()[0]
            if count < 10:
                esrs_data = [
                    # General
                    ("ESRS 2", "General Disclosures (Strategi, Governance, IRO)", "General", 1, 1),
                    # Environment
                    ("E1-1", "Transition plan for climate change mitigation", "E1 Climate", 1, 1),
                    ("E1-2", "Policies related to climate change", "E1 Climate", 1, 1),
                    ("E1-3", "Actions and resources in relation to climate change", "E1 Climate", 1, 1),
                    ("E1-4", "Targets related to climate change mitigation and adaptation", "E1 Climate", 1, 1),
                    ("E1-5", "Energy consumption and mix", "E1 Climate", 1, 1),
                    ("E1-6", "Gross Scopes 1, 2, 3 and Total GHG emissions", "E1 Climate", 1, 1),
                    ("E1-9", "Potential financial effects from material physical and transition risks", "E1 Climate", 1, 1),
                    ("E2-1", "Policies related to pollution", "E2 Pollution", 1, 1),
                    ("E3-1", "Policies related to water and marine resources", "E3 Water", 1, 1),
                    ("E3-4", "Water consumption", "E3 Water", 1, 1),
                    ("E4-1", "Transition plan on biodiversity and ecosystems", "E4 Biodiversity", 1, 1),
                    ("E5-1", "Policies related to resource use and circular economy", "E5 Circular Economy", 1, 1),
                    ("E5-5", "Resource outflows (Waste)", "E5 Circular Economy", 1, 1),
                    # Social
                    ("S1-1", "Policies related to own workforce", "S1 Own Workforce", 1, 1),
                    ("S1-4", "Taking action on material impacts on own workforce", "S1 Own Workforce", 1, 1),
                    ("S1-16", "Compensation metrics (Gender Pay Gap)", "S1 Own Workforce", 1, 1),
                    ("S2-1", "Policies related to workers in the value chain", "S2 Value Chain", 1, 1),
                    # Governance
                    ("G1-1", "Corporate culture and business conduct policies", "G1 Business Conduct", 1, 1),
                    ("G1-3", "Prevention and detection of corruption or bribery", "G1 Business Conduct", 1, 1)
                ]
                conn.executemany("INSERT OR REPLACE INTO f_ESRS_Requirements (esrs_code, disclosure_requirement, description, mandatory, applies_to_company) VALUES (?, ?, ?, ?, ?)", esrs_data)
                conn.commit()
        except sqlite3.Error as e:
            pass # Ignore if table issue, already logged above
init_db()

def show_page_help(title, content):
    with st.expander(f"📘 Guide: {title}", expanded=False):
        st.markdown(content)

if 'page' not in st.session_state: st.session_state.page = "Översikt"

# ============================================
# 5. PAGE FRAGMENTS
# ============================================

@st.fragment
def render_overview():
    badges = [
        {"text": "Regelefterlevnad: Översikt", "icon": "shield"},
        {"text": "CSRD Ready", "icon": "file"}
    ]
    skill_spotlight_header("Arbetsyta", "Översikt", badges)
    
    skill_ingress("""
    Välkommen till din centrala ESG-hub. Här samlar du, analyserar och rapporterar all hållbarhetsdata 
    för att möta kraven i CSRD, ISO och EcoVadis.
    """)
    
    # Data fetch
    with get_connection() as conn:
        s1 = pd.read_sql("SELECT SUM(co2_kg)/1000.0 as ton FROM f_Drivmedel", conn).iloc[0,0] or 0.0
        s2 = pd.read_sql("SELECT SUM(scope2_market_based_kg)/1000.0 as ton FROM f_Energi", conn).iloc[0,0] or 0.0
        s3 = pd.read_sql("SELECT SUM(co2e_tonnes) as ton FROM f_Scope3_Calculations", conn).iloc[0,0] or 0.0
        if s3 == 0.0:
             s3_travel = pd.read_sql("SELECT SUM(co2_kg)/1000.0 FROM f_Scope3_BusinessTravel", conn).iloc[0,0] or 0.0
             s3_waste = pd.read_sql("SELECT SUM(co2_kg)/1000.0 FROM f_Scope3_Waste", conn).iloc[0,0] or 0.0
             s3_purch = pd.read_sql("SELECT SUM(co2_kg)/1000.0 FROM f_Scope3_PurchasedGoodsServices", conn).iloc[0,0] or 0.0
             s3 = s3_travel + s3_waste + s3_purch

    # Readiness Score from GAP Analysis
    score, completed, total = governance.get_readiness_kpis()

    st.markdown('<div class="skill-grid-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: skill_card("Scope 1 (Ton)", f"{s1:.1f}")
    with c2: skill_card("Scope 2 (Ton)", f"{s2:.1f}")
    with c3: skill_card("Scope 3 (Ton)", f"{s3:.1f}")
    # Dynamic Readiness Score
    delta = f"{completed}/{total} Krav"
    with c4: skill_card("Readiness Score", f"{score:.0f}%", delta) 
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="skill-card">', unsafe_allow_html=True)
    st.subheader("Klimatfördelning (Scope 1-3)")
    fig = px.bar(x=["Scope 1", "Scope 2", "Scope 3"], y=[s1, s2, s3], 
                 color_discrete_sequence=["#1A33F5", "#7CF7F9", "#8A2BE2"])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color="#7CF7F9",
        title_font_color="#FFFFFF"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_strategy_gap():
    badges = [{"text": "GAP Analysis", "icon": "file"}]
    skill_spotlight_header("Strategi", "GAP-Analys & Krav", badges)
    
    score, completed, total = governance.get_readiness_kpis()
    st.progress(score / 100)
    st.caption(f"CSRD Readiness: {score:.1f}% ({completed} av {total} krav uppfyllda)")
    
    gap_df = governance.get_gap_analysis()
    
    if not gap_df.empty:
        # Use Data Editor for quick updates
        edited_df = st.data_editor(
            gap_df,
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Not Started", "In Progress", "Compliant", "N/A"],
                    required=True,
                ),
                "evidence_link": st.column_config.LinkColumn("Bevis"),
            },
            hide_index=True,
            use_container_width=True,
            key="gap_editor"
        )
        
        # Check for changes (Streamlit data editor doesn't auto-save to DB, need manual trigger or on_change)
        # For simplicity in this iteration, we add a "Save Changes" button that processes the edited_df
        if st.button("Spara ändringar"):
            # Iterate and update changed rows
            # Note: This is a bit heavy, in a real app we'd track diffs.
            # But for now, we just loop through and upsert.
            for index, row in edited_df.iterrows():
                governance.update_gap_status(
                    row['esrs_code'], 
                    row['status'], 
                    row['owner'], 
                    row['evidence_link'], 
                    row['notes']
                )
            st.success("GAP-analys uppdaterad!")
            st.rerun()

@st.fragment
def render_env_climate():
    badges = [
        {"text": "CSRD E1-6", "icon": "leaf"},
        {"text": "GHG Protocol", "icon": "leaf"},
        {"text": "ISO 14001", "icon": "shield"},
        {"text": "EcoVadis: ENV", "icon": "award"}
    ]
    skill_spotlight_header("Miljö", "Klimatdata", badges)
    
    st.info("Här registrerar du data för direkta utsläpp (Scope 1) och indirekta utsläpp från energi (Scope 2).")
    
    t1, t2 = st.tabs(["Scope 1: Fordon & Bränsle", "Scope 2: Energi"])
    
    with t1:
        with st.form("s1_form"):
            st.subheader("Registrera Drivmedel")
            datum = st.date_input("Datum")
            volym = st.number_input("Volym (Liter)", 0.0)
            typ = st.selectbox("Bränsletyp", ["Diesel (B7)", "Bensin (E10)", "HVO100", "E85"])
            if st.form_submit_button("Spara"):
                co2 = scope1_calculator.calculate_scope1(volym, typ)
                with get_connection() as conn:
                    conn.execute("INSERT INTO f_Drivmedel (datum, volym_liter, drivmedelstyp, co2_kg) VALUES (?, ?, ?, ?)", (datum, volym, typ, co2))
                    conn.commit()
                st.success(f"Registrerat! {co2:.2f} kg CO2e")
                st.rerun()
    with t2:
        st.write("Funktionalitet för energiregistrering kommer här.")

@st.fragment
def render_env_travel():
    badges = [
        {"text": "CSRD E1-6", "icon": "leaf"},
        {"text": "ISO 14001: Transport", "icon": "shield"}
    ]
    skill_spotlight_header("Miljö", "Resor & Transporter", badges)
    
    render_calc_travel_tabs()

@st.fragment
def render_env_water():
    badges = [
        {"text": "CSRD E3-4", "icon": "leaf"},
        {"text": "ISO 14001: Water", "icon": "shield"}
    ]
    skill_spotlight_header("Miljö", "Vattenhantering", badges)
    
    with st.form("water_form"):
        st.subheader("Registrera Vattenförbrukning")
        c1, c2 = st.columns(2)
        date = c1.date_input("Datum")
        withdrawal = c2.number_input("Uttag (m3)", 0.0)
        source = c1.selectbox("Källa", ["Kommunalt (Third-party)", "Grundvatten", "Ytvatten", "Annat"])
        discharge = c2.number_input("Utsläpp/Spillvatten (m3)", 0.0)
        dest = c1.selectbox("Mottagare", ["Avlopp (Sewer)", "Recipient (Sjö/Hav)", "Mark", "Annat"])
        recycled = c2.number_input("Återvunnet internt (m3)", 0.0)
        
        if st.form_submit_button("Spara Vattendata"):
            with get_connection() as conn:
                env_water.add_water_record(conn, date.strftime('%Y-%m-%d'), withdrawal, source, discharge, dest, recycled)
            st.success("Vattendata sparad!")
            st.rerun()
    
    with get_connection() as conn:
        df = env_water.get_water_data(conn)
        metrics = env_water.calculate_water_metrics(df)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: skill_card("Totalförbrukning (m3)", f"{metrics['total_consumption']:.1f}")
        with c2: skill_card("Vattenåtervinningsgrad", f"{metrics['recycling_rate']:.1f}%")
        with c3: skill_card("Totalt Uttag", f"{metrics['total_withdrawal']:.1f}")
        
        st.subheader("Historik")
        st.dataframe(df, hide_index=True, use_container_width=True)

@st.fragment
def render_env_waste():
    badges = [
        {"text": "CSRD E5-5", "icon": "leaf"},
        {"text": "ISO 14001: Waste", "icon": "shield"},
        {"text": "EcoVadis: ENV", "icon": "award"}
    ]
    skill_spotlight_header("Miljö", "Avfall & Cirkuläritet", badges)
    
    with st.form("waste_form"):
        st.subheader("Registrera Avfall")
        c1, c2 = st.columns(2)
        waste_date = c1.date_input("Datum")
        waste_type = c2.selectbox("Avfallstyp", ['Restavfall', 'Matavfall', 'Kartong/Papper', 'Plast', 'Farligt Avfall', 'Elektronik', 'Metall'])
        weight_kg = c1.number_input("Vikt (kg)", min_value=0.0, format="%.2f")
        is_hazardous = c2.checkbox("Farligt avfall")
        disposal_method = c1.selectbox("Behandlingsmetod", ['Återvinning', 'Reuse', 'Energiåtervinning', 'Förbränning (ej energi)', 'Deponi'])
        supplier = c2.text_input("Avfallsentreprenör")
        
        if st.form_submit_button("Spara Avfall"):
            with get_connection() as conn:
                env_waste.add_detailed_waste_record(conn, waste_date.strftime('%Y-%m-%d'), waste_type, is_hazardous, weight_kg, disposal_method, supplier)
            st.success("Avfallsdata registrerad!")
            st.rerun()

    with get_connection() as conn:
        df = env_waste.get_detailed_waste_data(conn)
        metrics = env_waste.calculate_waste_metrics(df)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: skill_card("Total mängd avfall (kg)", f"{metrics['total_weight']:.1f}")
        with c2: skill_card("Återvinningsgrad (%)", f"{metrics['recycling_rate']:.1f}%")
        with c3: skill_card("Andel farligt avfall", f"{metrics['hazardous_pct']:.1f}%")
        
        st.subheader("Registrerat Avfall")
        st.dataframe(df, hide_index=True, use_container_width=True)

@st.fragment
def render_social_hr():
    badges = [
        {"text": "CSRD S1-1", "icon": "users"},
        {"text": "S1-16 (Gender Pay)", "icon": "users"},
        {"text": "AFS 2001:1", "icon": "shield"},
        {"text": "EcoVadis: LAB", "icon": "award"}
    ]
    skill_spotlight_header("Socialt", "Egen Personal", badges)
    
    # Restored Logic from old render_hr
    tab1, tab2 = st.tabs(["👥 S1: Egen Personal", "📊 Historik"])
    with tab1:
        st.markdown('<div class="skill-card">', unsafe_allow_html=True)
        with st.form("hr_s1"):
            ar = st.number_input("År", 2025)
            c1, c2 = st.columns(2)
            kvinnor = c1.number_input("Antal Kvinnor i ledning", 0)
            man = c2.number_input("Antal Män i ledning", 0)
            
            total = kvinnor + man
            pct = (kvinnor / total * 100) if total > 0 else 0
            st.info(f"Beräknad andel kvinnor: {pct:.1f}%")
            
            enps = st.slider("eNPS", -100, 100, 0)
            if st.form_submit_button("Spara HR-data"):
                data = {'ar': ar, 'enps_intern': enps, 'ledning_kvinnor': kvinnor, 'ledning_man': man, 'employee_category': 'Internal'}
                social_tracker.save_extended_hr_data(data)
                st.success("Data sparad!")
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.write("Historik kommer här.")

@st.fragment
def render_gov_policy():
    badges = [
        {"text": "CSRD G1-1", "icon": "shield"},
        {"text": "ISO 9001", "icon": "file"},
        {"text": "EcoVadis: ETH", "icon": "award"}
    ]
    skill_spotlight_header("Styrning", "Policys & Dokument", badges)
    
    # Restored logic from old render_governance
    with st.form("gov_form"):
        name = st.text_input("Namn på policy")
        owner = st.text_input("Ägare")
        date = st.date_input("Fastställd")
        file = st.file_uploader("Bifoga dokument", type=["pdf", "doc", "docx"])
        if st.form_submit_button("Spara Policy"):
            doc_name = file.name if file else "Ingen fil"
            governance.add_policy(name, "1.0", owner, date, "G1", doc_name)
            st.success("Policy registrerad!")
            st.rerun()
    
    pols = governance.get_policies()
    if not pols.empty:
        st.dataframe(pols[['Status', 'policy_name', 'owner', 'next_review_date', 'document_link']], hide_index=True, use_container_width=True)

@st.fragment
def render_strategy_dma():
    badges = [
        {"text": "CSRD ESRS 2", "icon": "file"},
        {"text": "GRI 3", "icon": "file"}
    ]
    skill_spotlight_header("Strategi", "Väsentlighetsanalys", badges)
    
    t1, t2 = st.tabs(["Matris & Ämnen", "IRO (Risker & Möjligheter)"])
    
    with t1:
        show_page_help("Dubbel Väsentlighetsanalys (DMA)", """
        Bedöm varje hållbarhetsfråga utifrån två perspektiv:
        1. **Impact:** Påverkan på omvärlden.
        2. **Financial:** Finansiell risk för bolaget.
        """)
        dma_data = dma_tool.get_dma_data()
        
        if not dma_data.empty:
            fig = px.scatter(dma_data, x="financial_score", y="impact_score", text="topic", color="category", size_max=20, range_x=[0.5, 5.5], range_y=[0.5, 5.5])
            fig.add_hline(y=2.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            fig.add_vline(x=2.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#7CF7F9")
            st.plotly_chart(fig, use_container_width=True)

        with st.form("dma_form"):
            topic = st.text_input("Ämne")
            c1, c2 = st.columns(2)
            imp = c1.slider("Impact", 1, 5, 3)
            fin = c2.slider("Financial", 1, 5, 3)
            cat = st.selectbox("Kategori", ["Miljö", "Socialt", "Styrning"])
            if st.form_submit_button("Spara ämne"):
                dma_tool.add_dma_topic(topic, imp, fin, cat)
                st.rerun()
                
    with t2:
        if dma_data.empty:
            st.info("Lägg till väsentliga ämnen först.")
        else:
            sel_topic = st.selectbox("Välj Väsentligt Ämne", dma_data['topic'].unique())
            topic_id = dma_data[dma_data['topic'] == sel_topic]['id'].iloc[0]
            
            # Show existing IROs
            iros = dma_tool.get_iros(topic_id)
            if not iros.empty:
                st.dataframe(iros[['type', 'description', 'financial_effect']], hide_index=True, use_container_width=True)
            
            # Add new IRO
            with st.form("iro_form"):
                st.subheader(f"Lägg till IRO för {sel_topic}")
                iro_type = st.selectbox("Typ", ["Risk", "Möjlighet (Opportunity)", "Impact"])
                desc = st.text_area("Beskrivning")
                time_h = st.selectbox("Tidshorisont", ["Kort (<1 år)", "Medel (1-5 år)", "Lång (>5 år)"])
                fin_eff = st.text_input("Finansiell Effekt (Estimat)")
                
                if st.form_submit_button("Spara IRO"):
                    dma_tool.add_iro(topic_id, iro_type, desc, time_h, fin_eff)
                    st.success("IRO Sparad!")
                    st.rerun()

def render_calc_travel_tabs():
    t1, t2 = st.tabs(["🚌 Pendling", "✈️ Affärsresor"])
    with t1:
        c1, c2 = st.columns([1, 1])
        with c1:
            with st.expander("👤 Hantera Pendlingsprofiler"):
                 with st.form("add_person"):
                    profile_ref = st.text_input("Profil-referens", placeholder="Anställd A")
                    pnr = st.text_input("Hem-postnummer")
                    if st.form_submit_button("Spara Profil"):
                        with get_connection() as conn:
                            conn.execute("INSERT INTO d_Personal (fornamn, efternamn, hem_postnummer) VALUES (?, ?, ?)", (profile_ref, "Anonym", pnr))
                            conn.commit()
                        st.success("Sparad!")
                        st.rerun()
        st.info("Pendlingsmodulen är aktiv.")

    with t2:
        with st.form("business_travel_form"):
            st.subheader("Registrera Affärsresa")
            travel_date = st.date_input("Datum")
            travel_type = st.selectbox("Typ", ['Flight-Short', 'Flight-Medium', 'Flight-Long', 'Rail', 'Car'])
            distance_km = st.number_input("Distans (km)", min_value=0.0)
            
            fuel_type = st.selectbox("Bränsle (om bil)", ['Petrol', 'Diesel', 'Electric']) if travel_type == 'Car' else None
            class_type = st.selectbox("Klass (om flyg)", ['Economy', 'Business']) if 'Flight' in travel_type else 'Economy'
            
            if st.form_submit_button("Spara Resa"):
                co2_kg = scope3_travel.calculate_business_travel_emissions(travel_type, distance_km, fuel_type, class_type)
                with get_connection() as conn:
                    conn.execute("INSERT INTO f_Scope3_BusinessTravel (date, travel_type, distance_km, fuel_type, class_type, co2_kg) VALUES (?, ?, ?, ?, ?, ?)",
                                 (travel_date.strftime('%Y-%m-%d'), travel_type, distance_km, fuel_type, class_type, co2_kg))
                    conn.commit()
                st.success(f"Registrerad! {co2_kg:.2f} kg CO2.")

@st.fragment
def render_export():
    badges = [{"text": "Format: Excel / PDF", "icon": "file"}]
    skill_spotlight_header("Rapportering", "Export & Underlag", badges)
    
    # Restored logic from old render_reports
    t1, t2 = st.tabs(["📄 CSRD PDF/Excel", "🔍 ESRS Index"])
    with t1:
        st.info("Klicka nedan för att generera en Excel-rapport med all data for CSRD (Scope 1, 2, 3).")
        col_excel, col_pdf = st.columns(2)
        with col_excel:
            if st.button("Generera CSRD Rapport (Excel)"):
                try:
                    excel_file = report_csrd.generate_csrd_report()
                    st.download_button(
                        label="Ladda ner Excel-rapport",
                        data=excel_file,
                        file_name=f"CSRD_Report_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("Excel Rapport genererad!")
                except Exception as e:
                    st.error(f"Kunde inte generera Excel-rapport: {e}")
        with col_pdf:
            st.info("Klicka nedan för att generera en PDF-sammanfattning av CSRD-rapporten.")
            if st.button("Generera CSRD Sammanfattning (PDF)"):
                try:
                    # Fetch basic summary data for PDF (reusing what we have or logic from main generator)
                    # For simplicity in this quick fix, we call generate_csrd_report logic or similar
                    # But since generate_pdf_summary expects a DF, let's create a simple one here or fix report_csrd
                    # For now, let's just use a placeholder call as the PDF logic is complex to reconstruct inline
                    # and we prioritized Excel.
                    st.warning("PDF-generering uppdateras. Använd Excel-exporten för fullständig data.")
                except Exception as e:
                    st.error(f"Fel: {e}")

    with t2:
        idx_df = index_generator.get_esrs_index(2025)
        st.dataframe(idx_df, hide_index=True, use_container_width=True)

# ============================================
# 6. SIDEBAR & ROUTING (STRUCTURED)
# ============================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(124, 247, 249, 0.1); margin-bottom: 20px;">
            <h1 style="margin: 0; font-weight: 800; letter-spacing: -1px; color: #FFFFFF; font-size: 2.2rem;">ESG</h1>
            <p style="margin: 0; color: #7CF7F9; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 500;">
                Workspace
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    if st.button("🏠 Översikt", use_container_width=True, type="primary" if st.session_state.page == "Översikt" else "secondary"):
        st.session_state.page = "Översikt"
        st.rerun()
    
    st.markdown("<div style='margin-top:20px; color:#7CF7F9; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Miljö (E)</div>", unsafe_allow_html=True)
    if st.button("Klimatdata", use_container_width=True): st.session_state.page = "Klimatdata"; st.rerun()
    if st.button("Resor & Transport", use_container_width=True): st.session_state.page = "Resor"; st.rerun()
    if st.button("Vatten", use_container_width=True): st.session_state.page = "Vatten"; st.rerun()
    if st.button("Avfall", use_container_width=True): st.session_state.page = "Avfall"; st.rerun()

    st.markdown("<div style='margin-top:20px; color:#7CF7F9; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Socialt (S)</div>", unsafe_allow_html=True)
    if st.button("Egen Personal", use_container_width=True): st.session_state.page = "HR"; st.rerun()
    
    st.markdown("<div style='margin-top:20px; color:#7CF7F9; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Styrning (G)</div>", unsafe_allow_html=True)
    if st.button("Policys", use_container_width=True): st.session_state.page = "Policys"; st.rerun()
    if st.button("Väsentlighet (DMA)", use_container_width=True): st.session_state.page = "DMA"; st.rerun()
    if st.button("GAP-analys", use_container_width=True): st.session_state.page = "GAP"; st.rerun()

    st.markdown("<div style='margin-top:20px; color:#7CF7F9; font-size:0.8rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Rapport</div>", unsafe_allow_html=True)
    if st.button("Exportera", use_container_width=True): st.session_state.page = "Export"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    # Profile Card
    st.markdown(f"""
        <div style="background-color: rgb(15, 7, 45); border: 1px solid rgba(124, 247, 249, 0.1); border-radius: 8px; padding: 12px; display: flex; align-items: center; justify-content: space-between; margin-top: auto;">
            <div style="display: flex; align-items: center;">
                <div style="width: 32px; height: 32px; background-color: #1A33F5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; margin-right: 10px; font-size: 14px;">J</div>
                <div>
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 13px; line-height: 1.2;">J.M.</div>
                    <div style="color: #7CF7F9; font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Admin</div>
                </div>
            </div>
            <a href="?logout=1" target="_self" style="color: #FF4B4B; text-decoration: none; font-size: 18px;">⏻</a>
        </div>
    """, unsafe_allow_html=True)

# Routing Logic
if st.session_state.page == "Översikt": render_overview()
elif st.session_state.page == "Klimatdata": render_env_climate()
elif st.session_state.page == "Resor": render_env_travel()
elif st.session_state.page == "Vatten": render_env_water()
elif st.session_state.page == "Avfall": render_env_waste()
elif st.session_state.page == "HR": render_social_hr()
elif st.session_state.page == "Policys": render_gov_policy()
elif st.session_state.page == "DMA": render_strategy_dma()
elif st.session_state.page == "GAP": render_strategy_gap()
elif st.session_state.page == "Export": render_export()