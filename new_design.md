UI/UX-uppdatering v2.0: Skill Grafisk Profil (Advanced)
Denna guide implementerar en pixel-perfect tolkning av Skills grafiska profil, inklusive typografisk hierarki, 12-kolumners grid och organiska "Spotlight"-former.

Referens: SKILL-Grafisk-Identitet-v1.0_220216 (1).pdf

Steg 1: Konfigurera Temat (config.toml)
Vi behåller färgerna men säkerställer att vi använder rätt RGB-värden konverterade till HEX enligt manualen (s. 11).

Kommando:

Bash
mkdir -p .streamlit
nano .streamlit/config.toml
Innehåll:

Ini, TOML
[theme]
# Skill Blue (RGB 26, 51, 245) [cite: 109]
primaryColor = "#1A33F5"

# White - Ren bakgrund enligt manual [cite: 196]
backgroundColor = "#FFFFFF"

# Lilac (RGB 243, 233, 255) - Sekundär bakgrund [cite: 131]
secondaryBackgroundColor = "#F3E9FF"

# Indigo (RGB 21, 11, 63) - Textfärg för kontrast [cite: 129]
textColor = "#150B3F"

# Bas-font (vi överskriver detta med CSS sen)
font = "sans serif"
Steg 2: Avancerad CSS-injektion (dashboard.py)
Här implementerar vi typografisk hierarki (Uxum vs Neue Montreal) och organiska former. Vi använder CSS-variabler för att enkelt kunna justera grid och former.

Uppdatera din st.markdown-sektion i dashboard.py med följande:

Python
st.markdown("""
<style>
    /* --- 1. IMPORTERA TYPSNITT --- */
    /* Vi använder Inter med olika vikter för att simulera Skills typsnitt:
       - 800 (Extra Bold) -> Simulerar Uxum Grotesque Medium [cite: 253]
       - 300 (Light) -> Simulerar Uxum Grotesque Ultra Light (Ingress) [cite: 258]
       - 400 (Regular) -> Simulerar Neue Montreal Book (Brödtext) [cite: 263]
    */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;800&display=swap');

    :root {
        --skill-blue: #1A33F5;
        --skill-indigo: #150B3F;
        --skill-lilac: #F3E9FF;
        --skill-aqua: #7CF7F9;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--skill-indigo);
    }

    /* --- 2. TYPOGRAFISK HIERARKI --- */
    
    /* Rubriker (Uxum Medium-stil) [cite: 253] */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 800; 
        letter-spacing: -0.03em; /* Tight tracking likt Uxum */
        color: var(--skill-blue);
        text-transform: none; /* Uxum används oftast gement/sentence case i exemplen */
    }

    /* Ingress-klass (Används via HTML) [cite: 258] */
    .skill-ingress {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 1.25rem;
        line-height: 1.5;
        color: var(--skill-indigo);
        margin-bottom: 2rem;
        max-width: 800px;
    }

    /* --- 3. PEOPLE SPOTS & SPOTLIGHTS (FORMER) --- */
    /* Organiska former istället för perfekta cirklar [cite: 319, 449] */
    
    .people-spot {
        border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; /* "Blob"-form */
        overflow: hidden;
        box-shadow: 0 10px 20px rgba(26, 51, 245, 0.15);
        transition: all 0.5s ease-in-out;
    }
    
    .people-spot:hover {
        border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; /* Animeras vid hover */
    }

    /* Knappar (Rundade men distinkta) */
    div.stButton > button {
        background-color: var(--skill-blue);
        color: white;
        border-radius: 50px;
        padding: 12px 28px;
        font-weight: 600;
        border: none;
        transition: transform 0.2s;
    }
    
    div.stButton > button:hover {
        transform: scale(1.05);
        background-color: #0d21aa; /* Darker blue */
    }

    /* --- 4. GRID SYSTEM (12-col) --- */
    /* Manualen s. 29-30 beskriver 12 kolumner. 
       Vi skapar en CSS Grid-wrapper för custom layouts. */
    .skill-grid-container {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    .skill-col-span-6 { grid-column: span 6; }
    .skill-col-span-4 { grid-column: span 4; }
    .skill-col-span-12 { grid-column: span 12; }

    /* Kort-design för dashboard-element */
    .skill-card {
        background: white;
        padding: 24px;
        border-radius: 20px; /* Något mjukare hörn */
        border: 1px solid var(--skill-lilac);
        box-shadow: 0 4px 6px rgba(21, 11, 63, 0.05);
    }

</style>
""", unsafe_allow_html=True)
Steg 3: Python Hjälpfunktioner (Helpers)
För att enkelt använda "Ingress" och "Spotlight" utan att skriva HTML varje gång, lägg till dessa funktioner i dashboard.py:

Python
def skill_ingress(text):
    """Skriver ut en ingress i Uxum Ultra Light-stil (Inter 300)"""
    st.markdown(f'<p class="skill-ingress">{text}</p>', unsafe_allow_html=True)

def skill_spotlight_header(title, subtitle=None):
    """Skapar en header med Spotlight-grafik (SVG)"""
    # SVG baserat på sid 35 "People Spotlight"
    svg_blob = """
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="position:absolute; top:-20px; left:-20px; width:100px; opacity:0.1; z-index:0;">
      <path fill="#1A33F5" d="M44.7,-76.4C58.9,-69.2,71.8,-59.1,81.6,-46.6C91.4,-34.1,98.1,-19.2,95.8,-5.3C93.5,8.6,82.2,21.5,70.6,32.3C59,43.1,47.1,51.8,35.1,59.3C23.1,66.8,11,73.1,-2.4,77.3C-15.8,81.5,-30.5,83.6,-43.3,77.7C-56.1,71.8,-67,57.9,-75.4,43.4C-83.8,28.9,-89.7,13.8,-88.3,-0.8C-86.9,-15.4,-78.2,-29.5,-67.2,-41.2C-56.2,-52.9,-42.9,-62.2,-29.6,-69.8C-16.3,-77.4,-3,-83.3,10.2,-82.5L23.4,-81.7Z" transform="translate(100 100)" />
    </svg>
    """
    st.markdown(f"""
    <div style="position:relative; padding: 20px 0;">
        {svg_blob}
        <h1 style="position:relative; z-index:1; margin-bottom:0;">{title}</h1>
        {f'<p style="font-weight:500; color:#1A33F5; margin-top:0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def skill_card(title, value, delta=None):
    """Skapar ett kort enligt designsystemet"""
    delta_html = f'<span style="color:{"green" if "+" in str(delta) else "red"}; font-size:0.9em;">{delta}</span>' if delta else ""
    st.markdown(f"""
    <div class="skill-card">
        <h3 style="margin:0; font-size:1rem; color:#666;">{title}</h3>
        <div style="font-size:2rem; font-weight:800; color:#1A33F5;">
            {value} {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
Steg 4: Implementering i UI (Exempel)
Ersätt din nuvarande dashboard-kod med anrop till dessa funktioner för att se skillnaden.

Python
# Huvudrubrik med Spotlight-element
skill_spotlight_header("Hållbarhetsrapport 2024", "Skill ESG Workspace")

# Ingress (Uxum Ultra Light stil)
skill_ingress("""
Människor förändras. De utvecklas, och söker nya utmaningar. 
Detta verktyg hjälper oss att mäta och förstå den förändringen genom data.
""")

# Grid-system med kort
st.markdown('<div class="skill-grid-container">', unsafe_allow_html=True)

# Använd HTML inuti markdown för full kontroll över grid, eller använd st.columns
# Här simulerar vi Grid-klasser inuti st.columns för enkelhetens skull:
c1, c2, c3 = st.columns(3)
with c1:
    skill_card("CO2 Utsläpp", "288 ton", "-5%")
with c2:
    skill_card("Sjukfrånvaro", "0.82%", "-0.1%")
with c3:
    skill_card("Nöjdhet (eNPS)", "50", "+2")

st.markdown('</div>', unsafe_allow_html=True)
Checklista för kvalitetssäkring (Enligt Claude)
Kontrast: Vi använder #150B3F (Indigo) på vit bakgrund vilket ger utmärkt kontrast (WCAG AAA).

Former: .people-spot använder CSS border-radius med 4 värden för att skapa den "organiska" formen från s. 35.

Typografi: Vi skiljer nu tydligt på rubriker (Tjock/Bold) och Ingresser (Tunn/Light) enligt s. 16.