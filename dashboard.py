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
        st.markdown("<style>.stApp {background-color: #0A0E17; background-image: radial-gradient(circle at 50% 0%, #1a2642 0%, #0A0E17 70%);}</style>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br><br><h1 style='color:white; text-align:center;'>ESG <span style='color:#00E5FF;'>Admin</span></h1>", unsafe_allow_html=True)
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
# 2. THEME & STYLING (SAFE STRINGS)
# ============================================
if 'dark_mode' not in st.session_state: st.session_state['dark_mode'] = True

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
        background-image: VAR_BG_GRADIENT;
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
        transition: all 0.3s ease;
        align-items: center;
    }

    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: rgba(0, 229, 255, 0.15) !important;
        color: #00E5FF !important;
        border-left: 4px solid #00E5FF !important;
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

    .css-card {
        background-color: var(--bg-card);
        backdrop-filter: blur(12px);
        border: 1px solid VAR_CARD_BORDER;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: VAR_SHADOW;
    }
</style>
"""

css = css.replace("VAR_BG", theme['bg'])
css = css.replace("VAR_CARD_BG", theme['card_bg'])
css = css.replace("VAR_TEXT_MAIN", theme['text_main'])
css = css.replace("VAR_TEXT_MUTED", theme['text_muted'])
css = css.replace("VAR_BG_GRADIENT", theme['bg_gradient'])
css = css.replace("VAR_SIDEBAR_BG", theme['sidebar_bg'])
css = css.replace("VAR_CARD_BORDER", theme['card_border'])
css = css.replace("VAR_SHADOW", theme['shadow'])

st.markdown(css, unsafe_allow_html=True)

# ============================================
# 3. DB & HELPERS
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
            "CREATE TABLE IF NOT EXISTS f_ESRS_Requirements (esrs_code TEXT PRIMARY KEY, disclosure_requirement TEXT, description TEXT, mandatory INTEGER DEFAULT 1, applies_to_company INTEGER DEFAULT 1)"
        ]
        for sql in tables: conn.execute(sql)
        try: conn.execute("ALTER TABLE f_HR_Arsdata ADD COLUMN ledning_kvinnor INTEGER DEFAULT 0")
        except: pass
        try: conn.execute("ALTER TABLE f_HR_Arsdata ADD COLUMN ledning_man INTEGER DEFAULT 0")
        except: pass
        try: conn.execute("ALTER TABLE f_Scope3_Calculations ADD COLUMN product_name TEXT")
        except: pass

init_db()

def show_page_help(title, content):
    with st.expander(f"📘 Guide: {title}", expanded=False):
        st.markdown(content)

if 'page' not in st.session_state: st.session_state.page = "Översikt"

# ============================================
# 4. PAGE FRAGMENTS
# ============================================

@st.fragment
def render_overview():
    st.markdown('<h1 style="font-size: 2.5rem; font-weight: 800; color: var(--text-main);">Plattform för Hållbarhet & ESG</h1>', unsafe_allow_html=True)
    show_page_help("Översikt", "Här visas företagets totala klimatavtryck baserat på registrerad data.")
    
    with get_connection() as conn:
        s1 = pd.read_sql("SELECT SUM(co2_kg)/1000.0 as ton FROM f_Drivmedel", conn).iloc[0,0] or 0.0
        s2 = pd.read_sql("SELECT SUM(scope2_market_based_kg)/1000.0 as ton FROM f_Energi", conn).iloc[0,0] or 0.0
        s3 = pd.read_sql("SELECT SUM(co2e_tonnes) as ton FROM f_Scope3_Calculations", conn).iloc[0,0] or 0.0
        idx_data = index_generator.get_esrs_index(2024)
        readiness = index_generator.calculate_readiness_score(idx_data)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CO2 Scope 1", f"{s1:.1f} t")
    col2.metric("CO2 Scope 2", f"{s2:.1f} t")
    col3.metric("CO2 Scope 3", f"{s3:.1f} t")
    col4.metric("Readiness Score", f"{readiness:.0f}%")

    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Klimatfördelning")
    fig = px.bar(x=["Scope 1", "Scope 2", "Scope 3"], y=[s1, s2, s3], color=["#2962FF", "#00E5FF", "#7C4DFF"], title="Ton CO2e per Scope")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white" if st.session_state['dark_mode'] else "black")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_strategy():
    st.title("Strategi & Väsentlighet")
    show_page_help("DMA", "Identifiera och bedöm hållbarhetsfrågor (1-5).")
    dma_data = dma_tool.get_dma_data()
    
    if not dma_data.empty:
        fig = px.scatter(dma_data, x="financial_score", y="impact_score", text="topic", color="category", size_max=20, range_x=[0.5, 5.5], range_y=[0.5, 5.5])
        fig.add_hline(y=2.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig.add_vline(x=2.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white" if st.session_state['dark_mode'] else "black")
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

@st.fragment
def render_hr():
    st.title("HR & Social Hållbarhet")
    tab1, tab2 = st.tabs(["👥 S1: Egen Personal", "📊 Historik"])
    with tab1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        with st.form("hr_s1"):
            ar = st.number_input("År", 2024)
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

@st.fragment
def render_governance():
    st.title("Governance")
    show_page_help("Policys", "Ladda upp och bevaka era styrdokument.")
    
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
def render_calc():
    st.title("Beräkningar")
    t1, t2 = st.tabs(["🚌 Pendling", "💸 Inköp (Spend)"])
    with t1:
        st.info("Här beräknas pendlingsdata för konsulter.")
        if st.button("Kör pendlingsanalys"):
            with get_connection() as conn:
                res = scope3_pendling.calculate_all_consultants(conn)
                st.success(f"Beräknat {res['antal_uppdrag']} uppdrag. Totalt {res['total_co2_ton']:.1f} ton CO2.")
    with t2:
        with st.form("spend_form"):
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("Kategori", scope3_spend.get_categories())
            prod = c2.text_input("Produkt")
            sek = c3.number_input("Belopp (SEK)", 0.0)
            if st.form_submit_button("Spara inköp"):
                scope3_spend.add_spend_item(cat, "", prod, sek, "2024")
                st.success("Inköp sparat!")
        
        summ = scope3_spend.get_spend_summary("2024")
        if not summ.empty: st.dataframe(summ, hide_index=True, use_container_width=True)

@st.fragment
def render_reports():
    st.title("Rapporter")
    t1, t2 = st.tabs(["📄 CSRD PDF", "🔍 ESRS Index"])
    with t1:
        if st.button("Generera Fullständig PDF"):
            with get_connection() as conn:
                path = report_csrd.generate_csrd_report(conn, 2024)
                with open(path, "rb") as f: st.download_button("Ladda ner PDF", f, file_name="ESG_Report_2024.pdf")
    with t2:
        idx_df = index_generator.get_esrs_index(2024)
        st.dataframe(idx_df, hide_index=True, use_container_width=True)

@st.fragment
def render_settings():
    st.title("Inställningar")
    t1, t2, t3 = st.tabs(["💾 Datahantering", "🎨 Vy & Tema", "📤 Import"])
    with t1:
        with open(DB_PATH, "rb") as f:
            st.download_button(label="Ladda ner Systemfil (.db)", data=f, file_name="ESG_Data.db", type="primary", use_container_width=True)
    with t2:
        dark = st.toggle("Mörkt läge", value=st.session_state.dark_mode)
        if dark != st.session_state.dark_mode:
            st.session_state.dark_mode = dark
            st.rerun()
    with t3:
        st.file_uploader("Importera data", type=["xlsx", "pdf", "docx"])

# ============================================
# 5. MAIN ROUTING
# ============================================
with st.sidebar:
    # Sidebar Header
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
            <h1 style="margin: 0; font-weight: 800; letter-spacing: 3px; color: #FFFFFF; font-size: 2.2rem;">ESG</h1>
            <p style="margin: 0; color: #00E5FF; font-size: 0.75rem; letter-spacing: 1px; text-transform: uppercase; font-weight: 400;">
                Hållbarhetsindex
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    pages = ["Översikt", "Strategi (CSRD)", "HR-Data", "Governance", "Beräkningar", "Rapporter", "Inställningar"]
    for p in pages:
        if st.button(p, type="primary" if st.session_state.page == p else "secondary", use_container_width=True):
            st.session_state.page = p
            st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Premium Profile Card
    card_bg = "rgba(255, 255, 255, 0.05)" if st.session_state['dark_mode'] else "rgba(0, 0, 0, 0.05)"
    text_color = "white" if st.session_state['dark_mode'] else "#171717"
    st.markdown(f"""
        <div style="background-color: {card_bg}; border-radius: 16px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #2962FF, #00E5FF); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 12px; font-size: 16px;">J</div>
                <div>
                    <div style="color: {text_color}; font-weight: 700; font-size: 14px;">J.M.</div>
                    <div style="color: #00E5FF; font-size: 10px; font-weight: 600; text-transform: uppercase;">Administrator</div>
                </div>
            </div>
            <a href="?logout=1" target="_self" style="color: #FF4B4B; text-decoration: none; font-size: 18px; padding: 5px; border-radius: 8px; background: rgba(255,75,75,0.1); display: flex; align-items: center; justify-content: center; transition: 0.3s;">⏻</a>
        </div>
    """, unsafe_allow_html=True)

if st.session_state.page == "Översikt": render_overview()
elif st.session_state.page == "Strategi (CSRD)": render_strategy()
elif st.session_state.page == "HR-Data": render_hr()
elif st.session_state.page == "Governance": render_governance()
elif st.session_state.page == "Beräkningar": render_calc()
elif st.session_state.page == "Rapporter": render_reports()
elif st.session_state.page == "Inställningar": render_settings()
