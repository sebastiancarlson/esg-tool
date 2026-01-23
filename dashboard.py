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
    from modules import scope3_travel 
    from modules import scope3_waste 
    from modules import scope3_purchased_goods 
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel
    from modules import scope3_travel 
    from modules import scope3_waste 
    from modules import scope3_purchased_goods 

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
# 2. THEME & STYLING (DARK MODE: INDIGO/AQUA)
# ============================================
st.markdown("""
<style>
    /* --- 1. FONTS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;800&display=swap');

    :root {
        --skill-indigo: #150B3F;    /* Main Background */
        --skill-dark-indigo: #0F072D; /* Card/Sidebar Background */
        --skill-aqua: #7CF7F9;      /* Text / Accent */
        --skill-blue: #1A33F5;      /* Primary Action */
        --skill-violet: #8A2BE2;    /* Shapes / Secondary */
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
    
    /* --- 2. CARDS (Cleaner, refined look) --- */
    .skill-card {
        background: var(--skill-dark-indigo);
        padding: 20px; /* Slightly less padding */
        border-radius: 16px;
        border: 1px solid rgba(124, 247, 249, 0.05); /* Thinner, subtler border */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); /* Softer shadow */
        margin-bottom: 30px; /* Add spacing below cards */
    }
    
    .skill-card h3 {
        color: var(--skill-aqua) !important;
        opacity: 0.8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px; /* Space between title and content */
    }
    
    .skill-card div {
        color: var(--text-white); /* Value is white for pop */
    }

    /* --- 3. BUTTONS --- */
    div.stButton > button {
        background-color: var(--skill-blue);
        color: white;
        border-radius: 50px;
        border: none;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #7CF7F9; /* Aqua hover */
        color: #150B3F; /* Indigo text */
    }
    
    /* --- 4. SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: var(--skill-dark-indigo);
        border-right: 1px solid rgba(124, 247, 249, 0.05);
    }
    [data-testid="stSidebar"] h1 {
        color: var(--text-white);
    }
    
    /* --- 5. GRID --- */
    .skill-grid-container {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    /* Hide default Streamlit decoration if possible to clean up view */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- 6. BACKGROUND BLOBS (Aqua, Top & Bottom) --- */
    .stApp {
        background-image: 
            url('data:image/svg+xml;utf8,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath fill="%237CF7F9" fill-opacity="0.1" d="M42.9,-69.5C52.9,-60.3,56.6,-43.9,59.5,-29.5C62.4,-15.2,64.4,-2.8,62.8,9.1C61.2,21.1,56,32.6,48.9,44.3C41.7,56,32.6,68,20,74.8C7.3,81.6,-8.8,83.2,-23.2,79C-37.7,74.8,-50.4,64.8,-56.4,52.1C-62.4,39.4,-61.6,24.1,-66,8.2C-70.3,-7.8,-79.8,-24.3,-76.8,-36.9C-73.9,-49.5,-58.5,-58.2,-43.6,-65.3C-28.7,-72.3,-14.3,-77.7,1,-79.3C16.4,-80.9,32.8,-78.7,42.9,-69.5Z" transform="translate(100 100)" /%3E%3C/svg%3E'),
            url('data:image/svg+xml;utf8,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath fill="%237CF7F9" fill-opacity="0.1" d="M42.9,-69.5C52.9,-60.3,56.6,-43.9,59.5,-29.5C62.4,-15.2,64.4,-2.8,62.8,9.1C61.2,21.1,56,32.6,48.9,44.3C41.7,56,32.6,68,20,74.8C7.3,81.6,-8.8,83.2,-23.2,79C-37.7,74.8,-50.4,64.8,-56.4,52.1C-62.4,39.4,-61.6,24.1,-66,8.2C-70.3,-7.8,-79.8,-24.3,-76.8,-36.9C-73.9,-49.5,-58.5,-58.2,-43.6,-65.3C-28.7,-72.3,-14.3,-77.7,1,-79.3C16.4,-80.9,32.8,-78.7,42.9,-69.5Z" transform="translate(100 100)" /%3E%3C/svg%3E');
        background-repeat: no-repeat, no-repeat;
        background-position: top -40% center, bottom -40% right -20%;
        background-size: 110vw, 90vw;
        background-attachment: fixed, fixed;
    }

</style>
""", unsafe_allow_html=True)

# Removed the components.html block as we are now using CSS background-image

# ============================================
# 3. HELPERS
# ============================================

def skill_ingress(text):
    """Skriver ut en ingress (Inter 300)"""
    st.markdown(f'<p class="skill-ingress" style="font-size: 1.2rem;">{text}</p>', unsafe_allow_html=True)

def skill_spotlight_header(title, subtitle=None):
    """Skapar en header med Spotlight-grafik (Violet mot Indigo)"""
    svg_blob = """
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="position:absolute; top:-40px; left:-30px; width:140px; opacity:0.15; z-index:0;">
      <path fill="#8A2BE2" d="M44.7,-76.4C58.9,-69.2,71.8,-59.1,81.6,-46.6C91.4,-34.1,98.1,-19.2,95.8,-5.3C93.5,8.6,82.2,21.5,70.6,32.3C59,43.1,47.1,51.8,35.1,59.3C23.1,66.8,11,73.1,-2.4,77.3C-15.8,81.5,-30.5,83.6,-43.3,77.7C-56.1,71.8,-67,57.9,-75.4,43.4C-83.8,28.9,-89.7,13.8,-88.3,-0.8C-86.9,-15.4,-78.2,-29.5,-67.2,-41.2C-56.2,-52.9,-42.9,-62.2,-29.6,-69.8C-16.3,-77.4,-3,-83.3,10.2,-82.5L23.4,-81.7Z" transform="translate(100 100)" />
    </svg>
    """
    st.html(f"""
    <div style="position:relative; padding: 20px 0 40px 0;">
        {svg_blob}
        <h1 style="position:relative; z-index:1; margin-bottom:0; font-size: 3rem; color: #FFFFFF !important;">{title}</h1>
        {f'<p style="font-weight:500; color:#7CF7F9; margin-top:0; font-size: 1.1rem; text-transform:uppercase; letter-spacing:2px;">{subtitle}</p>' if subtitle else ''}
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
    """Visar strategisk affärsnytta kopplat till de 5 pelarna."""
    
    contexts = {
        "Översikt": {
            "risk": "Ger en helhetsbild av bolagets ESG-exponering, vilket minimerar risken för strategiska överraskningar från investerare eller kunder.",
            "effekt": "Centraliserad data minskar tiden för manuell rapportering och dubbelarbete vid upphandlingar.",
            "lag": "Säkerställer att ledningen har den överblick som krävs enligt aktiebolagslagens krav på bolagsstyrning.",
            "konk": "En transparent hållbarhetsprofil är idag en 'licence to operate' for att behålla och vinna stora kunder.",
            "hall": "Möjliggör datadrivna beslut för att styra hela verksamheten mot långsiktiga hållbarhetsmål."
        },
        "Strategi (CSRD)": {
            "risk": "Dubbel väsentlighetsanalys (DMA) identifierar dolda finansiella risker i klimatförändringar och leverantörskedjor.",
            "effekt": "Fokuserar resurserna på de frågor som faktiskt spelar roll, istället för att sprida insatserna tunt.",
            "lag": "Kärnan i CSRD (ESRS 2). Utan denna analys är ingen del av hållbarhetsrapporten laglig.",
            "konk": "Visar mognad och proaktivitet, vilket bygger förtroende hos banker (lägre ränta) och investerare.",
            "hall": "Säkerställer att affärsmodellen är robust och relevant även i en koldioxidneutral framtid."
        },
        "HR-Data": {
            "risk": "Systematisk uppföljning av arbetsmiljö minskar risken för dyra sjukskrivningar och arbetsrättsliga tvister.",
            "effekt": "Friska medarbetare med rätt kompetens är grunden för hög debiteringsgrad och lönsamhet.",
            "lag": "Uppfyller kraven i ESRS S1 (Egen personal) samt Diskrimineringslagen (Lönekartläggning).",
            "konk": "Stärkt Employer Brand attraherar topptalanger, vilket är den viktigaste tillgången i ett konsultbolag.",
            "hall": "Skapar en inkluderande arbetsplats som bidrar till social stabilitet och minskad ojämlikhet."
        },
        "Governance": {
            "risk": "Tydliga policys och visselblåsarsystem skyddar mot korruption, böter och varumärkeskador.",
            "effekt": "Tydliga ansvarsområden och processer (SOP:er) minskar intern byråkrati och osäkerhet.",
            "lag": "Krav enligt ESRS G1 (Affärsetik) samt Visselblåsarlagen.",
            "konk": "Kunder ställer allt högre krav på etiska riktlinjer i sina leverantörskoder (CoC).",
            "hall": "God bolagsstyrning är fundamentet för att långsiktigt kunna leverera på både miljö- och sociala mål."
        },
        "Beräkningar": {
            "risk": "Genom att mäta Scope 3 minskar risken för att bli utbytt av kunder som måste redovisa sina leverantörers utsläpp.",
            "effekt": "Identifierar 'hotspots' i inköp och resor där kostnadsbesparingar ofta går hand i hand med utsläppsminskningar.",
            "lag": "Uppfyller ESRS E1-6 (Gross Scopes 1, 2, 3 GHG emissions).",
            "konk": "Kan erbjuda kunder klimatneutrala konsulttjänster, en unik differentiator på marknaden.",
            "hall": "Konkretiserar miljöpåverkan och flyttar fokus från 'grönt prat' till mätbar action."
        },
        "Rapporter": {
            "risk": "Spårbarhet och audit trails minskar risken för anmärkningar vid extern revision.",
            "effekt": "Automatiserad rapportgenerering sparar hundratals timmar varje år jämfört med Excel-arbete.",
            "lag": "Säkerställer att den lagstadgade hållbarhetsrapporten (ÅRL) håller rätt format och kvalitet.",
            "konk": "En professionell rapport kan användas direkt i marknadsföring och säljpitchar.",
            "hall": "Transparens driver ansvar. Publicerade siffror skapar ett positivt tryck på organisationen att förbättra sig."
        }
    }

    ctx = contexts.get(module_name, contexts["Översikt"])

    with st.expander(f"💎 Strategiskt Affärsvärde: {module_name}", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**🛡️ Riskminimering**\n\n{ctx['risk']}")
            st.markdown(f"**⚖️ Efterlevnad (Compliance)**\n\n{ctx['lag']}")
            st.markdown(f"**🌱 Hållbarhet**\n\n{ctx['hall']}")
        with c2:
            st.markdown(f"**🚀 Effektivitet**\n\n{ctx['effekt']}")
            st.markdown(f"**🏆 Konkurrensfördel**\n\n{ctx['konk']}")


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
            "CREATE TABLE IF NOT EXISTS f_Scope3_PurchasedGoodsServices (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount_sek REAL, emission_factor_kg_per_sek REAL, co2_kg REAL)"
        ]
        for sql in tables: conn.execute(sql)
        
        # Populate ESRS Requirements if empty
        count = conn.execute("SELECT COUNT(*) FROM f_ESRS_Requirements").fetchone()[0]
        if count == 0:
            esrs_data = [
                ("E1-1", "Övergripande klimatstrategi", "Klimat", 1, 1),
                ("E1-6", "Växthusgasutsläpp (Scope 1, 2, 3)", "Klimat", 1, 1),
                ("E1-9", "Finansiella effekter av klimatrisker", "Klimat", 1, 1),
                ("S1-1", "Policyer för egen personal", "Socialt", 1, 1),
                ("S1-16", "Löneskillnader mellan könen (Gender Pay Gap)", "Socialt", 1, 1),
                ("G1-1", "Företagskultur och affärsetik", "Styrning", 1, 1),
                ("G1-3", "Förebyggande av korruption", "Styrning", 1, 1)
            ]
            conn.executemany("INSERT INTO f_ESRS_Requirements VALUES (?, ?, ?, ?, ?)", esrs_data)
            conn.commit()
        
        # Force update label for S1-16 if it was created with the old name
        conn.execute("UPDATE f_ESRS_Requirements SET disclosure_requirement = 'Löneskillnader mellan könen (Gender Pay Gap)' WHERE esrs_code = 'S1-16'")
        conn.commit()
            
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
# 5. PAGE FRAGMENTS
# ============================================

@st.fragment
def render_overview():
    # Header & Ingress
    skill_spotlight_header("Hållbarhet", "ESG Workspace")
    show_strategic_context("Översikt")
    skill_ingress("""
    Människor förändras. De utvecklas, och söker nya utmaningar. 
    Detta verktyg hjälper oss att mäta och förstå den förändringen genom data, 
    från klimatpåverkan till socialt ansvar.
    """)
    
    # Data fetch
    with get_connection() as conn:
        s1 = pd.read_sql("SELECT SUM(co2_kg)/1000.0 as ton FROM f_Drivmedel", conn).iloc[0,0] or 0.0
        s2 = pd.read_sql("SELECT SUM(scope2_market_based_kg)/1000.0 as ton FROM f_Energi", conn).iloc[0,0] or 0.0
        s3 = pd.read_sql("SELECT SUM(co2e_tonnes) as ton FROM f_Scope3_Calculations", conn).iloc[0,0] or 0.0
        idx_data = index_generator.get_esrs_index(2025)
        readiness = index_generator.calculate_readiness_score(idx_data)

    # Grid Layout with new Cards
    st.markdown('<div class="skill-grid-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: skill_card("Scope 1 (Ton)", f"{s1:.1f}")
    with c2: skill_card("Scope 2 (Ton)", f"{s2:.1f}")
    with c3: skill_card("Scope 3 (Ton)", f"{s3:.1f}")
    with c4: skill_card("Readiness Score", f"{readiness:.0f}%", "+5%") 
    st.markdown('</div>', unsafe_allow_html=True)

    # Chart
    st.markdown('<div class="skill-card">', unsafe_allow_html=True)
    st.subheader("Klimatfördelning")
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
def render_strategy():
    skill_spotlight_header("Strategi & Väsentlighet")
    show_strategic_context("Strategi (CSRD)")
    show_page_help("Dubbel Väsentlighetsanalys (DMA)", """
    Enligt lagkravet ESRS 2 räcker det inte att fråga vad intressenterna tycker är viktigt. Vi måste bedöma varje hållbarhetsfråga utifrån två perspektiv:
    
    1.  **Impact Materiality (Y-axeln):** Hur stor påverkan har verksamheten på människa och miljö?
    2.  **Financial Materiality (X-axeln):** Hur stor finansiell risk utgör frågan för verksamheten?
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

@st.fragment
def render_hr():
    skill_spotlight_header("HR & Social Hållbarhet")
    show_strategic_context("HR-Data")
    show_page_help("Skillnaden på S1 och S2", """
    *   **ESRS S1 (Egen personal):** Vår interna personal.
    *   **ESRS S2 (Arbetare i värdekedjan):** Våra uthyrda konsulter.
    """)
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

@st.fragment
def render_governance():
    skill_spotlight_header("Governance")
    show_strategic_context("Governance")
    
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
    skill_spotlight_header("Beräkningar")
    show_strategic_context("Beräkningar")
    t1, t2, t3, t4 = st.tabs(["🚌 Pendling", "✈️ Affärsresor", "🗑️ Avfall", "💸 Inköp (Spend)"]) # Added new tabs
    
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
                 with get_connection() as conn:
                    pers_df = pd.read_sql("SELECT person_id, fornamn as Profil, hem_postnummer as Postnummer FROM d_Personal", conn)
                    if not pers_df.empty: st.dataframe(pers_df, hide_index=True)

            with st.expander("🏢 Hantera Kundplatser"):
                with st.form("add_site"):
                    knamn = st.text_input("Kundens namn")
                    kpnr = st.text_input("Kundens postnummer")
                    if st.form_submit_button("Spara Kundplats"):
                        with get_connection() as conn:
                            conn.execute("INSERT INTO d_Kundsiter (kund_namn, postnummer) VALUES (?, ?)", (knamn, kpnr))
                            conn.commit()
                        st.success("Sparad!")
                        st.rerun()
                with get_connection() as conn:
                    site_df = pd.read_sql("SELECT * FROM d_Kundsiter", conn)
                    if not site_df.empty: st.dataframe(site_df, hide_index=True)
        with c2:
             with st.expander("📅 Skapa Pendlingsuppdrag", expanded=True):
                with get_connection() as conn:
                    pers_list = pd.read_sql("SELECT person_id, fornamn as namn FROM d_Personal", conn)
                    site_list = pd.read_sql("SELECT kund_plats_id, kund_namn FROM d_Kundsiter", conn)
                
                if not pers_list.empty and not site_list.empty:
                    with st.form("add_assignment"):
                        pid = st.selectbox("Välj Profil", options=pers_list['person_id'], format_func=lambda x: pers_list[pers_list['person_id']==x]['namn'].values[0])
                        sid = st.selectbox("Välj Kund/Site", options=site_list['kund_plats_id'], format_func=lambda x: site_list[site_list['kund_plats_id']==x]['kund_namn'].values[0])
                        start = st.date_input("Startdatum")
                        slut = st.date_input("Slutdatum", value=datetime.now())
                        dagar = st.slider("Arbetsdagar per vecka", 1.0, 7.0, 5.0)
                        dist = st.number_input("Manuell distans (valfri km, lämna 0 för automatik)", 0.0)
                        fard = st.selectbox("Färdmedel", ["Bil", "Elbil", "Buss", "Tåg", "Cykel", "Okänt"])
                        if st.form_submit_button("Spara Uppdrag"):
                            with get_connection() as conn:
                                conn.execute("INSERT INTO f_Uppdrag (person_id, kund_plats_id, startdatum, slutdatum, dagar_per_vecka, distans_km, fardmedel) VALUES (?, ?, ?, ?, ?, ?, ?)", (pid, sid, start.strftime('%Y-%m-%d'), slut.strftime('%Y-%m-%d'), dagar, dist if dist > 0 else None, fard))
                                conn.commit()
                            st.success("Sparad!")
                            st.rerun()
        
        st.markdown("---")
        if st.button("Kör pendlingsanalys", type="primary"):
            with get_connection() as conn:
                res = scope3_pendling.calculate_all_consultants(conn)
                if 'error' in res: st.error(res['error'])
                else: st.success(f"Klar! {res['total_co2_ton']:.2f} ton CO2.")
        
        with get_connection() as conn:
            calc_df = pd.read_sql("SELECT p.fornamn as Profil, k.kund_namn as Site, b.totalt_co2_kg as 'CO2 (kg)', b.datakvalitet as Kvalitet FROM f_Pendling_Beraknad b JOIN f_Uppdrag u ON b.uppdrag_id = u.uppdrag_id JOIN d_Personal p ON u.person_id = p.person_id JOIN d_Kundsiter k ON u.kund_plats_id = k.kund_plats_id", conn)
            if not calc_df.empty: st.dataframe(calc_df, hide_index=True, use_container_width=True)

    with t2:
        with st.form("business_travel_form"):
            st.subheader("Registrera Affärsresa")
            travel_date = st.date_input("Datum för resa")
            travel_type = st.selectbox("Typ av resa", ['Flight-Short', 'Flight-Medium', 'Flight-Long', 'Rail', 'Car'])
            distance_km = st.number_input("Distans (km)", min_value=0.0, format="%.2f")

            fuel_type = None
            class_type = 'Economy'

            if travel_type == 'Car':
                fuel_type = st.selectbox("Bränsletyp", ['Petrol', 'Diesel', 'Electric', 'Hybrid'])
            elif travel_type.startswith('Flight'):
                class_type = st.selectbox("Flygklass", ['Economy', 'Business', 'First'])
            
            if st.form_submit_button("Spara Affärsresa"):
                co2_kg = scope3_travel.calculate_business_travel_emissions(travel_type, distance_km, fuel_type, class_type)
                with get_connection() as conn:
                    conn.execute("INSERT INTO f_Scope3_BusinessTravel (date, travel_type, distance_km, fuel_type, class_type, co2_kg) VALUES (?, ?, ?, ?, ?, ?)",
                                 (travel_date.strftime('%Y-%m-%d'), travel_type, distance_km, fuel_type, class_type, co2_kg))
                    conn.commit()
                st.success(f"Affärsresa registrerad! Beräknade utsläpp: {co2_kg:.2f} kg CO2.")
                st.rerun()
        
        st.markdown("---")
        st.subheader("Registrerade Affärsresor")
        with get_connection() as conn:
            travel_df = pd.read_sql("SELECT date, travel_type, distance_km, fuel_type, class_type, co2_kg FROM f_Scope3_BusinessTravel", conn)
            if not travel_df.empty:
                st.dataframe(travel_df, hide_index=True, use_container_width=True)
            else:
                st.info("Inga affärsresor registrerade än.")

    with t3:
        with st.form("waste_form"):
            st.subheader("Registrera Avfall")
            waste_date = st.date_input("Datum för avfallshantering")
            waste_type = st.selectbox("Typ av avfall", ['General', 'Food', 'Paper/Cardboard', 'Plastics', 'Hazardous', 'Other'])
            weight_kg = st.number_input("Vikt (kg)", min_value=0.0, format="%.2f")
            disposal_method = st.selectbox("Avfallshanteringsmetod", ['Landfill', 'Recycled', 'Composted', 'Incinerated', 'Other'])
            
            if st.form_submit_button("Spara Avfall"):
                co2_kg = scope3_waste.calculate_waste_emissions(waste_type, weight_kg, disposal_method)
                with get_connection() as conn:
                    conn.execute("INSERT INTO f_Scope3_Waste (date, waste_type, weight_kg, disposal_method, co2_kg) VALUES (?, ?, ?, ?, ?)",
                                 (waste_date.strftime('%Y-%m-%d'), waste_type, weight_kg, disposal_method, co2_kg))
                    conn.commit()
                st.success(f"Avfall registrerat! Beräknade utsläpp: {co2_kg:.2f} kg CO2.")
                st.rerun()
        
        st.markdown("---")
        st.subheader("Registrerat Avfall")
        with get_connection() as conn:
            waste_df = pd.read_sql("SELECT date, waste_type, weight_kg, disposal_method, co2_kg FROM f_Scope3_Waste", conn)
            if not waste_df.empty:
                st.dataframe(waste_df, hide_index=True, use_container_width=True)
            else:
                st.info("Inget avfall registrerat än.")

    with t4:
        with st.form("purchased_goods_form"):
            st.subheader("Registrera Inköp av Varor & Tjänster")
            purchase_date = st.date_input("Datum för inköp")
            pg_category = st.selectbox("Kategori", ['IT Services', 'Office Supplies', 'Consulting', 'Other'])
            amount_sek = st.number_input("Totalt Belopp (SEK)", min_value=0.0, step=100.0, format="%.2f")
            
            if st.form_submit_button("Spara Inköp"):
                co2_kg = scope3_purchased_goods.calculate_purchased_goods_emissions(pg_category, amount_sek)
                with get_connection() as conn:
                    conn.execute("INSERT INTO f_Scope3_PurchasedGoodsServices (date, category, amount_sek, co2_kg) VALUES (?, ?, ?, ?)",
                                 (purchase_date.strftime('%Y-%m-%d'), pg_category, amount_sek, co2_kg))
                    conn.commit()
                st.success(f"Inköp registrerat! Beräknade utsläpp: {co2_kg:.2f} kg CO2.")
                st.rerun()
        
        st.markdown("---")
        st.subheader("Registrerade Inköp")
        with get_connection() as conn:
            purchased_goods_df = pd.read_sql("SELECT date, category, amount_sek, co2_kg FROM f_Scope3_PurchasedGoodsServices", conn)
            if not purchased_goods_df.empty:
                st.dataframe(purchased_goods_df, hide_index=True, use_container_width=True)
            else:
                st.info("Inga inköp registrerade än.")

@st.fragment
def render_reports():
    skill_spotlight_header("Rapporter")
    show_strategic_context("Rapporter")
    t1, t2 = st.tabs(["📄 CSRD PDF/Excel", "🔍 ESRS Index"])
    with t1:
        st.info("Klicka nedan för att generera en Excel-rapport med all data for CSRD (Scope 1, 2, 3).")
        col_excel, col_pdf = st.columns(2) # Create two columns for buttons
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
                    conn = get_connection()
                    
                    # Fetch all Scope 3 related dataframes
                    scope1_df = pd.read_sql("SELECT * FROM f_Drivmedel", conn) if "f_Drivmedel" in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn) else pd.DataFrame(columns=["datum", "volym_liter", "drivmedelstyp", "co2_kg"])
                    scope2_df = pd.read_sql("SELECT * FROM elforbrukning", conn) if "elforbrukning" in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn) else pd.DataFrame(columns=["datum", "kWh", "kostnad", "co2_kg"])
                    scope3_bus_travel_df = pd.read_sql("SELECT * FROM f_Scope3_BusinessTravel", conn) if "f_Scope3_BusinessTravel" in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn) else pd.DataFrame(columns=["date", "travel_type", "distance_km", "fuel_type", "class_type", "co2_kg"])
                    scope3_waste_df = pd.read_sql("SELECT * FROM f_Scope3_Waste", conn) if "f_Scope3_Waste" in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn) else pd.DataFrame(columns=["date", "waste_type", "weight_kg", "disposal_method", "co2_kg"])
                    scope3_purchased_goods_df = pd.read_sql("SELECT * FROM f_Scope3_PurchasedGoodsServices", conn) if "f_Scope3_PurchasedGoodsServices" in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn) else pd.DataFrame(columns=["date", "category", "amount_sek", "emission_factor_kg_per_sek", "co2_kg"])

                    # Summing up new Scope 3 categories
                    total_scope3_bus_travel = scope3_bus_travel_df["co2_kg"].sum() if not scope3_bus_travel_df.empty else 0
                    total_scope3_waste = scope3_waste_df["co2_kg"].sum() if not scope3_waste_df.empty else 0
                    total_scope3_purchased_goods = scope3_purchased_goods_df["co2_kg"].sum() if not scope3_purchased_goods_df.empty else 0

                    # Total Scope 3 emissions
                    total_scope3 = total_scope3_bus_travel + total_scope3_waste + total_scope3_purchased_goods

                    summary_data = {
                        "Scope": ["Scope 1", "Scope 2", "Scope 3"],
                        "Total CO2e (kg)": [
                            scope1_df["co2_kg"].sum() if not scope1_df.empty else 0,
                            scope2_df["co2_kg"].sum() if not scope2_df.empty else 0,
                            total_scope3 
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)

                    scope3_details = {
                        "Business Travel": total_scope3_bus_travel,
                        "Waste": total_scope3_waste,
                        "Purchased Goods & Services": total_scope3_purchased_goods
                    }

                    pdf_file = report_csrd.generate_pdf_summary(summary_df, scope3_details)
                    st.download_button(
                        label="Ladda ner PDF-sammanfattning",
                        data=pdf_file,
                        file_name=f"CSRD_Summary_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF Sammanfattning genererad!")
                except Exception as e:
                    st.error(f"Kunde inte generera PDF-sammanfattning: {e}")
                finally:
                    conn.close()
    with t2:
        idx_df = index_generator.get_esrs_index(2025)
        st.dataframe(idx_df, hide_index=True, use_container_width=True)

@st.fragment
def render_settings():
    skill_spotlight_header("Inställningar")
    t1, t2 = st.tabs(["💾 Datahantering", "📤 Import"])
    with t1:
        with open(DB_PATH, "rb") as f:
            st.download_button(label="Ladda ner Systemfil (.db)", data=f, file_name="ESG_Data.db", type="primary", use_container_width=True)
    with t2:
        st.file_uploader("Importera data", type=["xlsx", "pdf", "docx"])

# ============================================
# 6. SIDEBAR & ROUTING
# ============================================
with st.sidebar:
    # Sidebar Header with secret-compliant branding
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(124, 247, 249, 0.1); margin-bottom: 20px;">
            <h1 style="margin: 0; font-weight: 800; letter-spacing: -1px; color: #FFFFFF; font-size: 2.2rem;">ESG</h1>
            <p style="margin: 0; color: #7CF7F9; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 500;">
                Workspace
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    pages = ["Översikt", "Strategi (CSRD)", "HR-Data", "Governance", "Beräkningar", "Rapporter", "Inställningar"]
    for p in pages:
        if st.button(p, type="primary" if st.session_state.page == p else "secondary", use_container_width=True):
            st.session_state.page = p
            st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Profile Card (Dark theme)
    st.markdown(f"""
        <div style="background-color: #0F072D; border: 1px solid rgba(124, 247, 249, 0.1); border-radius: 8px; padding: 12px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center;">
                <div style="width: 32px; height: 32px; background-color: #1A33F5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; margin-right: 10px; font-size: 14px;">J</div>
                <div>
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 13px; line-height: 1.2;">J.M.</div>
                    <div style="color: #7CF7F9; font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Admin</div>
                </div>
            </div>
            <a href="?logout=1" target="_self" style="color: #FF4B4B; text-decoration: none; font-size: 11px; font-weight: 600;">LOGGA UT</a>
        </div>
    """, unsafe_allow_html=True)

if st.session_state.page == "Översikt": render_overview()
elif st.session_state.page == "Strategi (CSRD)": render_strategy()
elif st.session_state.page == "HR-Data": render_hr()
elif st.session_state.page == "Governance": render_governance()
elif st.session_state.page == "Beräkningar": render_calc()
elif st.session_state.page == "Rapporter": render_reports()
elif st.session_state.page == "Inställningar": render_settings()
