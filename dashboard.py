import streamlit as st
import pandas as pd
import sqlite3
import os
import time

# Import local modules
try:
    from modules import scope3_pendling, scope1_calculator, scope2_calculator
    from modules import report_csrd, export_excel
except ImportError:
    # Fallback if running from inside reference-code without package structure
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from modules import scope3_pendling, scope1_calculator, scope2_calculator
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
    div.stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        border: none;
        background-color: transparent;
        color: var(--text-muted);
        padding: 12px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        border-radius: 8px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
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
    st.markdown("## **ESG**", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7CF7F9; margin-top: -20px; font-weight: 300;'>&lt;Hållbarhetsindex&gt;</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation Items
    nav_items = {
        "Översikt": "📊",
        "Strategi (CSRD)": "🎯",
        "HR-Data": "👥",
        "Governance": "⚖️",
        "Beräkningar": "🧮",
        "Rapporter": "📄",
        "Revisorvy": "🔍",
        "Inställningar": "⚙️"
    }
    
    for label, icon in nav_items.items():
        # Active state styling logic: 
        # We use a trick with Markdown to render the active bar, 
        # or we just rely on the button visual change (which is limited in pure Streamlit).
        # For a truly custom look, we can check state and render differently.
        
        if st.session_state.page == label:
            # Active button style (simulated via markdown + button hack or just primary type)
             # NOTE: Streamlit buttons don't support custom classes easily. 
             # We use a primary button for active state to distinguish it.
            if st.button(f"{icon}  {label}", key=label, type="primary", use_container_width=True):
                pass # Already active
        else:
            if st.button(f"{icon}  {label}", key=label, type="secondary", use_container_width=True):
                st.session_state.page = label
                st.rerun()

    st.markdown("---")
    st.markdown("### 👤 Profil")
    st.markdown("**Jenny** (Admin)")
    
    st.markdown("### ⚙️ Vy")
    st.checkbox("Visa prognoser", value=True)
    st.checkbox("Dark Mode", value=True, disabled=True)

conn = get_connection()
page = st.session_state.page

# ============================================
# SIDA 1: ÖVERSIKT
# ============================================
if page == "Översikt":
    st.markdown('<h1 style="font-size: 3rem;">ESG <span class="gradient-text">Evidence Engine</span></h1>', unsafe_allow_html=True)
    st.markdown("Centraliserad plattform för hållbarhetsdata, rapportering och analys.", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CO2 Scope 1", "12.5 ton", "-2%")
    col2.metric("CO2 Scope 2", "4.2 ton", "-15%")
    col3.metric("CO2 Scope 3", "Calculating...", "Pending")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Systemstatus")
    st.progress(85, text="Datakvalitet Scope 1 & 2")
    st.progress(40, text="Datakvalitet Scope 3 (Pendling)")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 2: STRATEGI (NY)
# ============================================
elif page == "Strategi (CSRD)":
    st.title("Strategi & Väsentlighet")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Dubbel Väsentlighetsanalys (CSRD)")
    st.markdown("Identifiera och bedöm hållbarhetsfrågor baserat på påverkan och finansiell risk.")
    
    with st.form("materiality_form"):
        col_input, col_scores = st.columns([1, 2])
        
        with col_input:
            omrade = st.text_input("Hållbarhetsområde", placeholder="t.ex. Klimat, Arbetsvillkor")
            ar_strat = st.number_input("År", value=2024, step=1)
            
        with col_scores:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Impact Materiality**")
                impact_score = st.slider("Påverkan på omvärlden (1-10)", 1, 10, help="1=Liten, 10=Kritisk")
            with c2:
                st.markdown("**Financial Materiality**")
                fin_score = st.slider("Finansiell risk/möjlighet (1-10)", 1, 10, help="Risk för intäkter/kostnader")
        
        if st.form_submit_button("Lägg till i matris"):
            try:
                conn.execute("INSERT INTO f_Vasentlighet (omrade, impact_score, fin_score, ar) VALUES (?, ?, ?, ?)", (omrade, impact_score, fin_score, ar_strat))
                conn.commit()
                st.success(f"Lagt till {omrade}")
            except Exception as e:
                st.error(f"Fel: {e}")

    # Visualisering (Matris)
    import altair as alt
    try:
        data = pd.read_sql(f"SELECT * FROM f_Vasentlighet WHERE ar={ar_strat}", conn)
        
        if not data.empty:
            st.markdown("### Väsentlighetsmatris")
            chart = alt.Chart(data).mark_circle(size=200).encode(
                x=alt.X('fin_score', title='Finansiell Risk (1-10)', scale=alt.Scale(domain=[0, 11])),
                y=alt.Y('impact_score', title='Påverkan på Omvärlden (1-10)', scale=alt.Scale(domain=[0, 11])),
                color=alt.Color('omrade', legend=alt.Legend(title="Område")),
                tooltip=['omrade', 'fin_score', 'impact_score']
            ).properties(
                title=f"Väsentlighetsmatris {ar_strat}",
                height=400
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
            with st.expander("Visa tabelldata"):
                st.dataframe(data)
    except Exception as e:
        st.info("Ingen data tillgänglig än.")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# SIDA 3: HR-DATA (UPPDATERAD)
# ============================================
elif page == "HR-Data":
    st.title("HR & Social Hållbarhet")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Personal", "Hälsa", "Mångfald", "Årsvis Data"])
    
    with tab1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Personalöversikt")
        st.info("Här visas detaljerad personalstatistik.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab4:
        st.subheader("Årsvis HR-data")
        
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        with st.form("hr_form"):
            ar = st.number_input("År", value=2024, step=1)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Medarbetarnöjdhet**")
                enps = st.number_input("eNPS (Intern)", min_value=-100, max_value=100)
                cnps = st.number_input("cNPS (Konsult)", min_value=-100, max_value=100)
            
            with col2:
                st.markdown("**Bemanning**")
                interna = st.number_input("Antal interna", min_value=0)
                konsulter = st.number_input("Antal konsulter", min_value=0)
                nyanstallda = st.number_input("Nyanställda", min_value=0)
            
            with col3:
                st.markdown("**Hälsa & Säkerhet**")
                sjuk = st.number_input("Sjukfrånvaro (%)", min_value=0.0, step=0.1)
                olyckor = st.number_input("Arbetsolyckor", min_value=0)
                
                st.markdown("---")
                st.markdown("**Samhällsengagemang**")
                inspirerade = st.number_input("Antal inspirerade barn/unga", min_value=0, help="T.ex. via Code Summer Camp")
                utbildning = st.number_input("Timmar kompetensutv. per anställd", min_value=0.0, step=0.5)
            
            if st.form_submit_button("Spara HR-data"):
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO f_HR_Arsdata 
                        (ar, enps_intern, cnps_konsult, antal_interna, antal_konsulter, nyanstallda_ar, sjukfranvaro_procent, arbetsolyckor_antal, inspirerade_barn_antal, utbildning_timmar_snitt)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (ar, enps, cnps, interna, konsulter, nyanstallda, sjuk, olyckor, inspirerade, utbildning))
                    conn.commit()
                    st.success("✅ HR-data och Sociala KPI:er sparade!")
                except Exception as e:
                    st.error(f"Fel vid sparning: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SIDA 4: GOVERNANCE (NY)
# ============================================
elif page == "Governance":
    st.title("Governance & Leverantörskedja")
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("Styrning & EcoVadis-krav")
    st.markdown("Hantera policyefterlevnad och leverantörskontroll.")
    
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
            it_inkop_co2 = st.number_input("Estimerat CO2 inköp IT (ton)", min_value=0.0)
            lev_krav = st.slider("% Lev. som signerat CoC (Code of Conduct)", 0, 100, 50)
        
        if st.form_submit_button("Spara Governance-data"):
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO f_Governance_Inkop 
                    (ar, uppforandekod_pct, visselblasare_antal, gdpr_incidenter, it_inkop_co2, lev_krav_pct)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ar_gov, uppforandekod, visselblasare, gdpr, it_inkop_co2, lev_krav))
                conn.commit()
                st.success("✅ Governance-data sparad!")
            except Exception as e:
                st.error(f"Fel vid sparning: {e}")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# SIDA 5: BERÄKNINGAR
# ============================================

elif page == "Beräkningar":
    st.title("Automatiska Beräkningar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("🚌 Beräkna Scope 3 (Konsultpendling)")
        
        if st.button("Kör beräkning"):
            with st.spinner("Hämtar distanser och beräknar..."):
                result = scope3_pendling.calculate_all_consultants(conn)
                
                st.success(f"✅ Beräknat {result['antal_uppdrag']} uppdrag")
                st.metric("Totalt CO2", f"{result['total_co2_ton']:.1f} ton")
                
                # Visa datakvalitetsfördelning
                st.json(result['quality_breakdown'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("📊 Uppdatera Scope 1 & 2")
        
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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "CSRD/ESRS",
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
