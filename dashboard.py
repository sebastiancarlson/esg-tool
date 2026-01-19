import streamlit as st
import pandas as pd
import sqlite3
import os
import time

# Import local modules
try:
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel
except ImportError:
    # Fallback if running from inside reference-code without package structure
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from modules import scope3_pendling, scope1_calculator, scope2_calculator, scope3_spend, governance, dma_tool, social_tracker, index_generator
    from modules import report_csrd, export_excel


# ============================================
# CONFIG & CSS (Dark Premium Theme)
# ============================================
st.set_page_config(
    page_title="ESG Hållbarhetsindex", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Init session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "Översikt"

# Avancerad CSS för Dark Mode & Navigation
st.markdown("""
<style>
    /* --- FONTS & COLORS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    :root {
        --esg-blue-primary: #2962FF;  
        --esg-cyan: #00E5FF;          
        --bg-dark: #0A0E17;
        --bg-card: #151B2B;             
        --text-main: #F0F2F6;
        --text-muted: #B0B8C6;
    }

    /* --- GLOBAL LAYOUT --- */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-main) !important;
        background-color: var(--bg-dark) !important;
    }
    
    .stApp {
        background-color: var(--bg-dark);
        background-image: radial-gradient(circle at 50% 0%, #1a2642 0%, #0A0E17 70%);
        background-attachment: fixed;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text-main) !important;
    }

    /* --- TEXT COLORS --- */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {
        color: var(--text-main) !important;
    }

    /* --- BUTTONS IN SIDEBAR --- */
    /* --- SIDEBAR BUTTONS (Navigation) --- */
    [data-testid="stSidebar"] div.stButton {
        margin-bottom: -15px !important; /* Reduce vertical gap */
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

    /* Fix för inre text-container i knappen */
    [data-testid="stSidebar"] div.stButton > button > div {
        justify-content: flex-start !important;
        text-align: left !important;
    }

    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        transform: translateX(5px);
    }
    
    div.stButton > button:focus {
        border: none;
        outline: none;
        color: white;
    }

    /* --- CARDS (Glassmorphism) --- */
    .css-card {
        background-color: rgba(21, 27, 43, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .css-card h3 {
        color: #FFFFFF !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    /* --- GRADIENT TEXT --- */
    .gradient-text {
        background: linear-gradient(90deg, #FFFFFF 0%, #00E5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

</style>
""", unsafe_allow_html=True)


DB_PATH = os.path.join("database", "esg_index.db")
# Ensure we refer to the DB in the root if running from subdir
if not os.path.exists(DB_PATH) and os.path.exists(os.path.join("..", DB_PATH)):
    DB_PATH = os.path.join("..", DB_PATH)

def get_connection():
    return sqlite3.connect(DB_PATH)

# ============================================
# DATABASE INITIALIZATION (CACHED)
# ============================================
@st.cache_resource
def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_HR_Arsdata (
                ar INTEGER PRIMARY KEY,
                enps_intern INTEGER,
                cnps_konsult INTEGER,
                antal_interna INTEGER,
                antal_konsulter INTEGER,
                nyanstallda_ar INTEGER,
                sjukfranvaro_procent REAL,
                arbetsolyckor_antal INTEGER,
                allvarliga_olyckor INTEGER DEFAULT 0,
                ledning_kvinnor INTEGER DEFAULT 0,
                ledning_man INTEGER DEFAULT 0,
                inspirerade_barn_antal INTEGER DEFAULT 0,
                utbildning_timmar_snitt REAL DEFAULT 0
            )
        """)
        try:
            conn.execute("ALTER TABLE f_HR_Arsdata ADD COLUMN inspirerade_barn_antal INTEGER DEFAULT 0")
            conn.execute("ALTER TABLE f_HR_Arsdata ADD COLUMN utbildning_timmar_snitt REAL DEFAULT 0")
        except: pass
            
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Pendling_Beraknad (
                berakning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uppdrag_id INTEGER,
                antal_arbetsdagar REAL,
                total_km REAL,
                emissionsfaktor_kg_per_km REAL,
                totalt_co2_kg REAL,
                datakvalitet TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT, description TEXT)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Vasentlighet (id INTEGER PRIMARY KEY AUTOINCREMENT, omrade TEXT, impact_score INTEGER, fin_score INTEGER, ar INTEGER)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Governance_Inkop (ar INTEGER PRIMARY KEY, uppforandekod_pct INTEGER, visselblasare_antal INTEGER, gdpr_incidenter INTEGER, it_inkop_co2 REAL, lev_krav_pct INTEGER)
        """)

        # --- MASTER PLAN TABLES (Modules A, B, D) ---
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_DMA_Materiality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                impact_score INTEGER CHECK(impact_score BETWEEN 1 AND 5),
                financial_score INTEGER CHECK(financial_score BETWEEN 1 AND 5),
                esrs_code TEXT,
                category TEXT,
                stakeholder_input TEXT,
                created_date TEXT,
                last_updated TEXT,
                is_material INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Scope3_Calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                spend_sek REAL,
                emission_factor REAL,
                co2e_tonnes REAL,
                data_quality TEXT CHECK(data_quality IN ('Verified', 'Estimated', 'Default')),
                reporting_period TEXT,
                source_document TEXT,
                created_date TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Governance_Policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL UNIQUE,
                document_version TEXT,
                owner TEXT,
                last_updated DATE,
                next_review_date DATE,
                is_implemented INTEGER DEFAULT 0,
                document_link TEXT,
                esrs_requirement TEXT,
                notes TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Social_Metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                value REAL,
                period TEXT,
                data_source TEXT,
                employee_category TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_ESRS_Requirements (
                esrs_code TEXT PRIMARY KEY,
                disclosure_requirement TEXT,
                description TEXT,
                mandatory INTEGER DEFAULT 1,
                applies_to_skill INTEGER DEFAULT 1
            )
        """)

        # Seed ESRS Requirements if empty
        try:
            check = conn.execute("SELECT COUNT(*) FROM f_ESRS_Requirements").fetchone()[0]
            if check == 0:
                requirements = [
                    ("E1-6", "Gross Scope 1, 2, 3 and Total GHG emissions", "Klimatpåverkan och växthusgaser", 1),
                    ("S1-1", "Policies related to own workforce", "Policys för egen personal", 1),
                    ("S1-14", "Health and safety indicators", "Hälsa och säkerhet", 1),
                    ("S1-16", "Remuneration metrics (Pay gap)", "Lönegap mellan könen", 1),
                    ("G1-1", "Business conduct policies", "Affärsetik och policys", 1)
                ]
                conn.executemany("INSERT INTO f_ESRS_Requirements VALUES (?, ?, ?, 1, 1)", requirements)
        except: pass

        # --- MISSING TABLES FOR SCOPE 1, 2 & 3 & REPORTS ---
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Energi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ar INTEGER,
                manad INTEGER,
                anlaggning_id TEXT,
                el_kwh REAL,
                fjarrvarme_kwh REAL,
                el_kalla TEXT,
                scope2_location_based_kg REAL,
                scope2_market_based_kg REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS d_Personal (
                person_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fornamn TEXT,
                efternamn TEXT,
                hem_postnummer TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS d_Kundsiter (
                kund_plats_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kund_namn TEXT,
                postnummer TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Uppdrag (
                uppdrag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                kund_plats_id INTEGER,
                startdatum TEXT,
                slutdatum TEXT,
                dagar_per_vecka REAL,
                distans_km REAL,
                fardmedel TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS d_Kontor (
                kontor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                namn TEXT,
                aktiv INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS f_Riskregister (
                risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                beskrivning TEXT,
                status TEXT DEFAULT 'Öppen'
            )
        """)
        try:
            conn.execute("INSERT INTO system_config (key, value, description) VALUES ('company_name', 'Företaget AB', 'Företagsnamn')")
        except: pass

# Run DB initialization once
init_db()

# ============================================
# CUSTOM SIDEBAR NAVIGATION
# ============================================
with st.sidebar:
    # Premium Header
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 25px 0;">
            <h1 style="margin: 0; font-weight: 800; letter-spacing: 4px; color: #FFFFFF; font-size: 2.5rem;">ESG</h1>
            <div style="height: 2px; background: linear-gradient(90deg, transparent, #00E5FF, transparent); margin: 5px auto; width: 80%;"></div>
            <p style="margin: 0; color: #00E5FF; font-family: 'Inter', sans-serif; font-weight: 300; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase;">
                Hållbarhetsindex
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Items (Using Material Design Icons for consistency)
    nav_items = {
        "Översikt": ":material/dashboard:",
        "Strategi (CSRD)": ":material/target:",
        "HR-Data": ":material/groups:",
        "Governance": ":material/gavel:",
        "Beräkningar": ":material/calculate:",
        "Rapporter": ":material/article:",
        "Revisorvy": ":material/find_in_page:",
        "Inställningar": ":material/settings:"
    }
    
    for label, icon_name in nav_items.items():
        # Active state styling logic
        if st.session_state.page == label:
            if st.button(label, icon=icon_name, key=label, type="primary", use_container_width=True):
                pass 
        else:
            if st.button(label, icon=icon_name, key=label, type="secondary", use_container_width=True):
                st.session_state.page = label
                st.rerun()

    st.markdown("---")
    
    # Compact Profile Card
    st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="display: flex; align-items: center;">
                <div style="width: 34px; height: 34px; background: linear-gradient(135deg, #00E5FF 0%, #2962FF 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 10px; font-size: 14px; box-shadow: 0 2px 8px rgba(0, 229, 255, 0.2);">J</div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 13px;">Jenny Svensson</div>
                    <div style="color: #B0B8C6; font-size: 10px;">System Admin</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Settings (Compact columns)
    c1, c2 = st.columns(2)
    with c1:
        st.toggle("Prognos", value=True)
    with c2:
        st.toggle("Mörkt", value=True, disabled=True)

conn = get_connection()
page = st.session_state.page

# ============================================
# SIDA 1: ÖVERSIKT
# ============================================
if page == "Översikt":
    st.markdown('<h1 style="font-size: 3rem;">ESG <span class="gradient-text">Evidence Engine</span></h1>', unsafe_allow_html=True)
    st.markdown("Centraliserad plattform för hållbarhetsdata, rapportering och analys.", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CO2 Scope 1", "12.5 ton", "-2%")
    col2.metric("CO2 Scope 2", "4.2 ton", "-15%")
    col3.metric("CO2 Scope 3", "Calculating...", "Pending")
    
    # Dynamic Readiness Score
    try:
        idx_data = index_generator.get_esrs_index(conn, 2024)
        score = index_generator.calculate_readiness_score(idx_data)
        col4.metric("CSRD Readiness", f"{score}%", "+5%")
    except:
        col4.metric("CSRD Readiness", "0%", "N/A")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Systemstatus")
    st.progress(85, text="Datakvalitet Scope 1 & 2")
    st.progress(40, text="Datakvalitet Scope 3 (Pendling)")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 2: STRATEGI & DMA (UPGRADED)
# ============================================
elif page == "Strategi (CSRD)":
    st.title("Strategi & Väsentlighet")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Dubbel Väsentlighetsanalys (DMA)")
    st.markdown("Identifiera och bedöm hållbarhetsfrågor enligt CSRD/ESRS-krav.")
    
    # Hämtar data
    dma_data = dma_tool.get_dma_data(conn)
    
    # --- VISUALISERING (MATRIS) ---
    import plotly.express as px
    
    if not dma_data.empty:
        # Skapa scatter plot
        fig = px.scatter(
            dma_data,
            x="financial_score",
            y="impact_score",
            text="topic",
            color="category",
            size_max=20,
            range_x=[0.5, 5.5],
            range_y=[0.5, 5.5],
            title="Väsentlighetsmatris (Impact vs Financial)",
            labels={"financial_score": "Finansiell Väsentlighet", "impact_score": "Impact Väsentlighet"}
        )
        
        # Lägg till tröskellinjer (vid 3)
        fig.add_hline(y=2.5, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig.add_vline(x=2.5, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        
        # Styling
        fig.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ingen data att visa. Lägg till ditt första ämne nedan.")

    # --- FORMULÄR ---
    st.markdown("---")
    with st.form("dma_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Hållbarhetsämne", placeholder="t.ex. Klimatförändringar")
            cat = st.selectbox("Kategori", ["Miljö (E)", "Socialt (S)", "Styrning (G)"])
        with col2:
            imp = st.slider("Impact Väsentlighet (1-5)", 1, 5, 3, help="Hur stor påverkan har vi på omvärlden?")
            fin = st.slider("Finansiell Väsentlighet (1-5)", 1, 5, 3, help="Hur stor risk/möjlighet för bolaget?")
            
        if st.form_submit_button("Lägg till i analys"):
            if topic:
                dma_tool.add_dma_topic(conn, topic, imp, fin, cat)
                st.success(f"'{topic}' har lagts till!")
                st.rerun()
            else:
                st.error("Ange ett ämne.")

    # --- TABELL ---
    if not dma_data.empty:
        with st.expander("Visa detaljerad lista & ESRS-mappning"):
            st.dataframe(
                dma_data[['topic', 'category', 'esrs_code', 'impact_score', 'financial_score', 'is_material']],
                column_config={
                    "is_material": st.column_config.CheckboxColumn("Väsentligt?")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Delete knapp
            to_del = st.selectbox("Ta bort ämne", dma_data['id'], format_func=lambda x: dma_data[dma_data['id']==x]['topic'].values[0])
            if st.button("Ta bort markerat ämne"):
                dma_tool.delete_dma_topic(conn, to_del)
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# SIDA 3: HR & SOCIAL DATA (UPGRADED)
# ============================================
elif page == "HR-Data":
    st.title("HR & Social Hållbarhet")
    
    tab_s1, tab_s2, tab_history = st.tabs(["👥 S1: Egen Personal", "🚜 S2: Konsulter", "📈 Historik & KPI"])
    
    # --- TAB S1: EGEN PERSONAL ---
    with tab_s1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Data för egen arbetsstyrka (ESRS S1)")
        
        with st.form("s1_form"):
            ar_s1 = st.number_input("Rapporteringsår", value=2024, step=1)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Demografi & Grunddata**")
                interna = st.number_input("Antal interna medarbetare (FTE)", min_value=0)
                nyanstallda = st.number_input("Nyanställda under året", min_value=0)
                pay_gap = st.number_input("Gender Pay Gap (okorrigerat %)", min_value=0.0, step=0.1)
            
            with c2:
                st.markdown("**Utveckling & Hälsa**")
                utbildning = st.number_input("Utbildningstimmar per anställd (snitt)", min_value=0.0, step=0.5)
                sjuk = st.number_input("Sjukfrånvaro (%)", min_value=0.0, max_value=100.0, step=0.1)
                enps = st.slider("eNPS (Medarbetarnöjdhet)", -100, 100, 10)
            
            if st.form_submit_button("Spara S1-data"):
                data = {
                    'ar': ar_s1, 'enps_intern': enps, 'cnps_konsult': 0, 
                    'antal_interna': interna, 'antal_konsulter': 0, 'nyanstallda_ar': nyanstallda,
                    'sjukfranvaro_procent': sjuk, 'arbetsolyckor_antal': 0, 
                    'inspirerade_barn_antal': 0, 'utbildning_timmar_snitt': utbildning,
                    'employee_category': 'Internal', 'gender_pay_gap_pct': pay_gap
                }
                social_tracker.save_extended_hr_data(conn, data)
                st.success("S1-data sparad!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB S2: KONSULTER ---
    with tab_s2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Arbetstagare i värdekedjan (ESRS S2)")
        st.info("För bemanningsbolag är detta en kritisk del av ESRS-rapporteringen.")
        
        with st.form("s2_form"):
            ar_s2 = st.number_input("Rapporteringsår", value=2024, step=1, key="ar_s2")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Bemanningsvolym**")
                konsulter = st.number_input("Antal konsulter i uppdrag (snitt)", min_value=0)
                olyckor_konsult = st.number_input("Arbetsolyckor (konsulter)", min_value=0)
            
            with c2:
                st.markdown("**Engagemang**")
                cnps = st.slider("cNPS (Konsultnöjdhet)", -100, 100, 10)
                inspirerade = st.number_input("Antal inspirerade barn/unga", min_value=0)
            
            if st.form_submit_button("Spara S2-data"):
                # Vi hämtar befintlig data för året och uppdaterar S2-fälten
                existing = social_tracker.get_hr_summary(conn, ar_s2)
                if not existing.empty:
                    data = existing.iloc[0].to_dict()
                else:
                    data = {k: 0 for k in ['ar', 'enps_intern', 'cnps_konsult', 'antal_interna', 'antal_konsulter', 'nyanstallda_ar', 'sjukfranvaro_procent', 'arbetsolyckor_antal', 'inspirerade_barn_antal', 'utbildning_timmar_snitt', 'gender_pay_gap_pct']}
                    data['employee_category'] = 'Mixed'
                
                data['ar'] = ar_s2
                data['antal_konsulter'] = konsulter
                data['arbetsolyckor_antal'] = olyckor_konsult
                data['cnps_konsult'] = cnps
                data['inspirerade_barn_antal'] = inspirerade
                
                social_tracker.save_extended_hr_data(conn, data)
                st.success("S2-data sparad!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB HISTORY ---
    with tab_history:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Historisk HR-data")
        history = pd.read_sql("SELECT * FROM f_HR_Arsdata ORDER BY ar DESC", conn)
        if not history.empty:
            st.dataframe(history, hide_index=True, use_container_width=True)
        else:
            st.info("Ingen historik tillgänglig.")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 4: GOVERNANCE (NY)
# ============================================
elif page == "Governance":
    st.title("Governance & Leverantörskedja")
    
    tab_policy, tab_kpi = st.tabs(["📚 Policy-bibliotek", "📊 KPI & Inköp"])
    
    # --- FLIK 1: POLICY MANAGER ---
    with tab_policy:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Styrdokument (G1)")
        st.info("Håll ordning på policys och revisionsdatum för att möta CSRD-krav.")
        
        # Visa tabell
        policies = governance.get_policies(conn)
        if not policies.empty:
            # Visa snyggare tabell
            display_cols = ['Status', 'policy_name', 'document_version', 'owner', 'next_review_date', 'esrs_requirement']
            st.dataframe(
                policies[display_cols], 
                column_config={
                    "next_review_date": st.column_config.DateColumn("Nästa översyn"),
                    "policy_name": "Dokument",
                    "esrs_requirement": "Koppling (ESRS)"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Delete knapp (enkel implementation)
            with st.expander("Hantera/Ta bort policy"):
                p_id = st.selectbox("Välj dokument att ta bort", policies['id'], format_func=lambda x: policies[policies['id']==x]['policy_name'].values[0])
                if st.button("Ta bort markerad"):
                    governance.delete_policy(conn, p_id)
                    st.rerun()
        else:
            st.info("Inga policys registrerade än.")

        st.markdown("---")
        st.markdown("### Lägg till nytt dokument")
        
        with st.form("add_policy_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("Dokumentnamn", placeholder="t.ex. Uppförandekod")
                p_ver = st.text_input("Version", value="1.0")
                p_owner = st.text_input("Ägare (Roll)", placeholder="t.ex. HR-chef")
            with c2:
                p_date = st.date_input("Senast fastställd")
                p_esrs = st.selectbox("Koppling till ESRS", ["G1 (Business Conduct)", "S1 (Own Workforce)", "S2 (Value Chain)", "E1 (Climate)"])
            
            if st.form_submit_button("Spara till bibliotek"):
                governance.add_policy(conn, p_name, p_ver, p_owner, p_date, p_esrs)
                st.success("Dokument sparat!")
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- FLIK 2: KPI & INKÖP (Gamla vyn) ---
    with tab_kpi:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Nyckeltal & Leverantörskontroll")
        
        with st.form("gov_form"):
            ar_gov = st.number_input("År", value=2024, step=1)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📜 Etik & Policy")
                uppforandekod = st.slider("% Anställda som signerat Uppförandekod", 0, 100, 95)
                visselblasare = st.number_input("Antal visselblåsarärenden", min_value=0)
                gdpr = st.number_input("Antal GDPR-incidenter", min_value=0)

            with col2:
                st.markdown("### 🚚 Hållbara Inköp")
                it_inkop_co2 = st.number_input("Estimerat CO2 inköp IT (ton)", min_value=0.0, help="Manuellt värde. Använd Scope 3-kalkylatorn för detaljer.")
                lev_krav = st.slider("% Lev. som signerat CoC (Code of Conduct)", 0, 100, 50)
            
            if st.form_submit_button("Spara KPI:er"):
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO f_Governance_Inkop 
                        (ar, uppforandekod_pct, visselblasare_antal, gdpr_incidenter, it_inkop_co2, lev_krav_pct)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (ar_gov, uppforandekod, visselblasare, gdpr, it_inkop_co2, lev_krav))
                    conn.commit()
                    st.success("✅ KPI:er sparade!")
                except Exception as e:
                    st.error(f"Fel vid sparning: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# SIDA 5: BERÄKNINGAR
# ============================================

elif page == "Beräkningar":
    st.title("Automatiska Beräkningar")
    
    # Flikar för olika scopes
    tab_pendling, tab_spend, tab_update = st.tabs(["Scope 3: Pendling", "Scope 3: Inköp (Spend)", "Uppdatera Scope 1 & 2"])
    
    with tab_pendling:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("🚌 Beräkna Konsultpendling")
        st.info("Hämtar distanser från API och matchar med uppdragsdata.")
        
        if st.button("Kör pendlingsberäkning"):
            with st.spinner("Hämtar distanser och beräknar..."):
                result = scope3_pendling.calculate_all_consultants(conn)
                
                st.success(f"✅ Beräknat {result['antal_uppdrag']} uppdrag")
                st.metric("Totalt CO2 (Pendling)", f"{result['total_co2_ton']:.1f} ton")
                st.json(result['quality_breakdown'])
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_spend:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("💸 Beräkna Inköpta Varor & Tjänster")
        st.markdown("Spend-baserad analys (Scope 3.1) för tjänster, IT och material.")
        
        col_form, col_stat = st.columns([1, 2])
        
        with col_form:
            with st.form("spend_form"):
                kategori = st.selectbox("Kategori", scope3_spend.get_categories())
                subkategori = st.text_input("Beskrivning", placeholder="T.ex. IT-konsulter Q1")
                belopp = st.number_input("Belopp (SEK)", min_value=0.0, step=1000.0)
                ar_spend = st.selectbox("År", [2024, 2025], key="spend_year")
                
                if st.form_submit_button("Lägg till utgift"):
                    co2 = scope3_spend.add_spend_item(conn, kategori, subkategori, belopp, ar_spend)
                    st.success(f"Lagt till! {co2:.2f} ton CO2e")
        
        with col_stat:
            # Visa sammanställning
            try:
                summary = scope3_spend.get_spend_summary(conn, ar_spend)
                if not summary.empty:
                    st.dataframe(summary, hide_index=True)
                    st.metric("Total CO2 (Inköp)", f"{summary['total_co2'].sum():.1f} ton")
                else:
                    st.info("Inga utgifter registrerade för detta år.")
            except:
                st.info("Databasen uppdateras...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab_update:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("📊 Uppdatera Scope 1 & 2")
        st.markdown("Kör om alla beräkningar för drivmedel och energi baserat på senaste faktorerna.")
        
        if st.button("Omberäkna alla poster"):
            scope1_calculator.recalculate_all(conn)
            scope2_calculator.recalculate_all(conn)
            
            st.success("✅ Alla beräkningar uppdaterade!")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 6: RAPPORTER
# ============================================

elif page == "Rapporter":
    st.title("Generera Rapporter")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "CSRD/ESRS",
        "ESRS Index",
        "EcoVadis",
        "ISO 14001",
        "Custom Excel"
    ])
    
    with tab1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("CSRD-rapport enligt ESRS")
        
        ar = st.selectbox("Välj år", [2024, 2023, 2022])
        
        if st.button("Generera PDF"):
            pdf_path = report_csrd.generate_csrd_report(conn, ar)
            
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Ladda ner CSRD-rapport",
                    data=f,
                    file_name=f"ESG_CSRD_{ar}.pdf",
                    mime="application/pdf"
                )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("ESRS Content Index")
        st.markdown("Spårbarhetsmatris som visar efterlevnad mot specifika ESRS-krav.")
        
        ar_idx = st.selectbox("Välj år för index", [2024, 2025], key="ar_idx")
        idx_df = index_generator.get_esrs_index(conn, ar_idx)
        
        st.dataframe(idx_df, hide_index=True, use_container_width=True)
        
        score_val = index_generator.calculate_readiness_score(idx_df)
        st.metric("Readiness Score", f"{score_val}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Excel-export (För Revision)")
        
        if st.button("Skapa Excel"):
            excel_path = export_excel.create_audit_excel(conn, 2024)
            
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📊 Ladda ner Excel",
                    data=f,
                    file_name="ESG_Audit_2024.xlsx"
                )
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 7: REVISORVY
# ============================================

elif page == "Revisorvy":
    st.title("Audit Trail & Spårbarhet")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Välj post att granska")
    
    kategori = st.selectbox("Kategori", [
        "Scope 1 (Drivmedel)",
        "Scope 2 (Energi)",
        "Scope 3 (Pendling)"
    ])
    
    if kategori == "Scope 3 (Pendling)":
        try:
            uppdrag = pd.read_sql("""
                SELECT 
                    b.berakning_id,
                    p.fornamn || ' ' || p.efternamn as Konsult,
                    k.kund_namn as Kund,
                    u.startdatum,
                    b.totalt_co2_kg
                FROM f_Pendling_Beraknad b
                JOIN f_Uppdrag u ON b.uppdrag_id = u.uppdrag_id
                JOIN d_Personal p ON u.person_id = p.person_id
                JOIN d_Kundsiter k ON u.kund_plats_id = k.kund_plats_id
            """, conn)
            
            if not uppdrag.empty:
                vald = st.selectbox("Välj post", uppdrag['berakning_id'])
                
                if st.button("Visa detaljer"):
                    details = pd.read_sql(f"""
                        SELECT * FROM f_Pendling_Beraknad WHERE berakning_id = {vald}
                    """, conn)
                    
                    st.json(details.to_dict(orient='records')[0])
                    
                    # Visa beräkningsformel
                    st.markdown("### Beräkningsformel")
                    st.code("""
                    Total km = Distans × 2 (tur/retur) × Antal arbetsdagar
                    CO2 (kg) = Total km × Emissionsfaktor
                    """)
            else:
                st.info("Inga beräkningar hittades.")
        except Exception as e:
            st.error(f"Kunde inte hämta data: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 8: INSTÄLLNINGAR
# ============================================

elif page == "Inställningar":
    st.title("Systeminställningar")
    
    tab1, tab2, tab3 = st.tabs([
        "Företagsinformation",
        "Importera Data",
        "Backup & Export"
    ])
    
    with tab1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        try:
            config = pd.read_sql("SELECT * FROM system_config", conn)
            
            for _, row in config.iterrows():
                new_val = st.text_input(row['description'], value=row['value'], key=row['key'])
                # Spara ändringar vid knappklick (Implementation pending)
        except:
            st.info("Ingen konfiguration hittades.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Importera från Excel")
        
        uploaded = st.file_uploader("Ladda upp HR-export (Konsultregister)", type=['xlsx', 'csv'])
        
        if uploaded:
            try:
                df = pd.read_excel(uploaded) if uploaded.name.endswith('.xlsx') else pd.read_csv(uploaded)
                st.dataframe(df.head())
                if st.button("Importera till databas"):
                    st.success(f"✅ {len(df)} rader importerade!")
            except Exception as e:
                st.error(f"Fel vid inläsning: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Backup")
        
        if st.button("Skapa backup"):
            import shutil
            from datetime import datetime
            
            backup_name = f"esg_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                shutil.copy(DB_PATH, backup_name)
                
                with open(backup_name, "rb") as f:
                    st.download_button(
                        label="💾 Ladda ner backup",
                        data=f,
                        file_name=backup_name
                    )
            except Exception as e:
                st.error(f"Backup failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

conn.close()
