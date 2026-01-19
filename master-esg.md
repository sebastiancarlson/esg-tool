# GAP-ANALYS & APP-SPECIFIKATION: SKILL ESG WORKSPACE

## 1. Jämförelseanalys: Toyota MH vs. Skill

### Toyota Material Handling (TMH) - "Best Practice"
* **Strategi:** CSRD/ESRS-anpassad. Genomför formell **Dubbel Väsentlighetsanalys (DMA)** med strukturerad Impact vs Financial Risk-bedömning.
* **Miljö:** Vetenskapliga mål (SBTi). Detaljerad redovisning av hela värdekedjan (Scope 1, 2 & 3, inklusive inköpta varor & tjänster). Transparenta emissionsberäkningar med verifierade källor.
* **Socialt:** Tydlig uppdelning av risker för egen personal (S1) och arbetstagare i värdekedjan (S2). Systematisk datainsamling för ESRS-nyckeltal (lönegap, utbildning, arbetsmiljö).
* **Styrning:** Detaljerad struktur för ESG-kommittéer och policyhantering. Versionshantering och regelbunden review-process för alla styrdokument.

### Skill - "Nuläge"
* **Strategi:** Inspirerad av GRI/ÅRL. Tematisk struktur (Fokus: Socialt/Kompetens). Saknar formell väsentlighetsanalys enligt CSRD-krav.
* **Miljö:** Grundläggande. Fokus på kontorsel (Scope 2) och egna fordon (Scope 1). Saknar komplett Scope 3-beräkning för inköp och tjänster. Mycket data baseras på schabloner.
* **Socialt:** Stark på "mjuka värden" (trivsel, kultur). Saknar viss systematik kring datainsamling enligt ESRS (t.ex. lönegap, uppdelning intern personal vs konsulter).
* **Styrning:** Informell. Beskrivande snarare än strukturerad process. Saknar systematik för policyuppdatering och efterlevnad.

---

## 2. Identifierade Gap (Vad Skill saknar)

1. **Avsaknad av DMA:** Ingen formell Double Materiality Assessment för att identifiera väsentliga hållbarhetsfrågor (Impact vs. Financial risk). CSRD kräver denna som grund för hela rapporten.
2. **Ofullständig Scope 3:** Saknar beräkningar för inköpta varor & tjänster (ofta största utsläppskällan för tjänstebolag). Endast pendling är delvis kartlagd.
3. **Dataprecision:** Mycket data baseras på schabloner ("räknat i överkant"). Behov av bättre spårbarhet och flaggning av datakvalitet (Verifierad vs Estimerad).
4. **S1/S2-separation:** HR-data blandar intern personal och konsulter, vilket försvårar korrekt ESRS-rapportering (egen arbetsstyrka vs värdekedja).
5. **Policy-styrning:** Saknar systematik för implementering och uppföljning av policys (Governance) på detaljnivå. Ingen versionshantering eller automatiska review-påminnelser.

---

## 3. Specifikation: Verktyg & Funktioner för Workspace

För att brygga gapet ska appen (`dashboard.py` extension) innehålla följande moduler.

### 🛠 Modul A: DMA Tool (Double Materiality Assessment)

**Funktion:** Ett interaktivt gränssnitt där användaren:
* Lägger till hållbarhetsämnen (fritext, ex: "Kompetensförsörjning")
* Skattar varje ämne på två skalor (1-5):
  * **Impact Materiality:** Hur stor påverkan har Skill på samhälle/miljö inom detta område?
  * **Financial Materiality:** Hur stor finansiell risk/möjlighet innebär detta för Skill?
* Får automatiska ESRS-kodförslag baserat på nyckelord (ex: "kompetens" → S1, "leverantör" → S2)
* Visualiserar resultatet i en **Scatter Plot Matrix** med väsentlighetströskel (≥3 på någon dimension)
* Exporterar resultat som CSV för vidare arbete

**Motivering:** Krav i CSRD (ESRS 2). Ersätter "magkänsla" med strukturerad data och styr hela rapportens innehåll. Dokumenterar processen för revisorer.

**Teknisk implementation:**
* Databas: `f_DMA_Materiality` (topic, impact_score, financial_score, esrs_code, is_material)
* Visualisering: Plotly scatter plot med röd "väsentlig zon"
* Logik: Keyword-baserad ESRS-mappning (14 standarder: E1-E5, S1-S4, G1)

---

### 🌍 Modul B: Carbon Cockpit (Scope 3 Expansion)

**Funktion:** Utöka nuvarande emissionskalkylatorer med:
* **Spend-based analysis** för inköp:
  * Input: Spend (SEK) per kategori (IT-tjänster, Konsulter, Kontorsmaterial, Resor)
  * Logik: Multiplicera med emissionsfaktorer (hårdkodade från DEFRA/EPA)
  * Output: Total CO2e för "Purchased Goods & Services" (GHG Kategori 1)
* **Datakvalitetsflaggor:**
  * ✅ Verifierad (data från leverantör)
  * ⚠️ Estimerad (spend-based beräkning)
  * ❌ Schablon (branschgenomsnitt)
* **Visualisering:** Stacked bar chart som visar fördelning mellan Scope 1, 2 och 3-kategorier
* **KPI-tracking:** Scope 3 som % av totala utsläpp

**Motivering:** För att nå EcoVadis Guld/Platinum krävs full koll på värdekedjans utsläpp. Scope 3 Kategori 1 är ofta 60-80% av tjänstebolags totala klimatpåverkan.

**Teknisk implementation:**
* Databas: `f_Scope3_Calculations` (category, spend_sek, emission_factor, co2e_tonnes, data_quality)
* Emissionsfaktorer: Dictionary med SEK → tCO2e-omvandling per kategori
* Integration: Koppla till DMA (varna om E1 är väsentlig men Scope 3 saknas)

---

### 👥 Modul C: Social Data Tracker (HR & S1/S2)

**Funktion:** Import och strukturering av HR-data mot ESRS-krav:
* **S1 (Egen personal):**
  * Gender Pay Gap (okorrigerat, enligt ESRS S1-16)
  * Utbildningstimmar per medarbetarkategori
  * Arbetsmiljöincidenter (frekvens, allvarlighetsgrad)
  * Anställningsförhållanden (tillsvidare vs tidsbegränsat)
* **S2 (Konsulter i värdekedjan):**
  * Antal konsulter per kund/uppdrag
  * Uppföljning av arbetsmiljö hos kund
  * Leverantörskrav och uppföljning
* **Uppdelning:** Tydlig kategorisering i databas (employee_category: "Internal" / "Consultant")
* **Visualisering:** Dashboard med nyckeltal och trendlinjer

**Motivering:** Standardiserar datainsamlingen och säkerställer att man inte missar obligatoriska ESRS-nyckeltal. Kritiskt för bemanningsbolag att skilja på S1 och S2.

**Teknisk implementation:**
* Uppdatera befintlig tabell: `f_HR_Arsdata` (lägg till kolumn: employee_category)
* Ny tabell: `f_Social_Metrics` (metric_type, value, period, data_source)
* Import-funktion: CSV-upload med validering mot ESRS-schema

---

### ⚖️ Modul D: Governance & Policy Manager

**Funktion:** Ett bibliotek för styrdokument som automatiskt flaggar status:
* **Policy-inventering:**
  * Policy Name (ex: "Uppförandekod")
  * Document Version (ex: "v2.1")
  * Owner (ansvarig person/roll)
  * Last Updated (senaste revision)
  * Next Review Date (auto-beräknas: Last Updated + 12 månader)
  * Is Implemented (checkbox: "Aktiv i organisationen")
* **Varningssystem:**
  * 🔴 Röd varning om Next Review Date har passerats
  * 🟡 Gul varning om review inom 30 dagar
* **ESRS-mappning:** Koppla varje policy till relevant ESRS-krav (ex: Anti-korruptionspolicy → G1-3)
* **Audit trail:** Loggar alla ändringar i versionshistorik

**Motivering:** Governance-delen (G1) kräver ordning och reda. Systemet ska proaktivt varna om en viktig policy är för gammal. Kritiskt för CSRD-compliance.

**Teknisk implementation:**
* Databas: `f_Governance_Policies` (policy_name, version, owner, last_updated, next_review_date, is_implemented)
* Automatik: Beräkna next_review_date vid varje uppdatering
* UI: Tabell med färgkodade rader baserat på status

---

### 📑 Modul E: Index Generator

**Funktion:** En motor som mappar insamlad data till färdigt ESRS/GRI Content Index:
* **Input:** Hämtar data från Modul A-D
* **Mappning:**
  * DMA-resultat → ESRS 2 (Disclosure Requirements)
  * Scope 3-data → E1-6 (Climate Change)
  * HR-data → S1-10 till S1-17 (Own Workforce)
  * Policys → G1-1 till G1-6 (Business Conduct)
* **Output:**
  * Tabell med kolumner: ESRS Disclosure | Status | Sida i rapport | Kommentar
  * Status: ✅ Rapporterad | ⚠️ Delvis | ❌ Ej tillämplig (med motivering)
* **Export:** PDF/Excel med clickable länkar till underliggande data

**Motivering:** Slutprodukten. Gör rapporten reviderbar och transparent för kunder, revisorer och myndigheter. Visar tydligt var Skill står i CSRD-compliance.

**Teknisk implementation:**
* Referenstabell: `f_ESRS_Requirements` (esrs_code, disclosure_req, description, mandatory)
* Join-logik: Matcha data från alla moduler mot ESRS-krav
* Template: Markdown → HTML → PDF-konvertering

---

## 4. Datamodell (SQLite Schema)

### Nya tabeller

```sql
-- Modul A: Double Materiality Assessment
CREATE TABLE f_DMA_Materiality (
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
);

-- Modul B: Scope 3 Calculations
CREATE TABLE f_Scope3_Calculations (
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
);

-- Modul D: Governance Policies
CREATE TABLE f_Governance_Policies (
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
);

-- Modul E: ESRS Requirements (referenstabell)
CREATE TABLE f_ESRS_Requirements (
    esrs_code TEXT PRIMARY KEY,
    disclosure_requirement TEXT,
    description TEXT,
    mandatory INTEGER DEFAULT 1,
    applies_to_skill INTEGER DEFAULT 1
);
```

### Uppdateringar av befintliga tabeller

```sql
-- Modul C: Lägg till i befintlig HR-tabell
ALTER TABLE f_HR_Arsdata ADD COLUMN employee_category TEXT DEFAULT 'Internal';
ALTER TABLE f_HR_Arsdata ADD COLUMN gender_pay_gap_pct REAL;
ALTER TABLE f_HR_Arsdata ADD COLUMN training_hours_per_employee REAL;
```

---

## 5. Implementation Roadmap

### Fas 1: Foundation (Vecka 1-2)
1. ✅ Modul A: DMA Tool (FÄRDIG KOD TILLGÄNGLIG)
2. 🔄 Modul D: Governance Tracker (enklast att bygga parallellt)
3. 🔄 Skapa databas-schema för alla moduler

### Fas 2: Data Collection (Vecka 3-4)
4. 🔄 Modul B: Scope 3 Calculator
5. 🔄 Modul C: Social Data Tracker (kräver HR-datainsamling)
6. 🔄 Integration mellan moduler (DMA styr vilka moduler som är obligatoriska)

### Fas 3: Reporting (Vecka 5-6)
7. 🔄 Modul E: Index Generator
8. 🔄 PDF-export med ESRS-struktur
9. 🔄 Dashboard-översikt ("CSRD Readiness Score")

---

## 6. Tekniska Krav

### Tech Stack
* **Backend:** Python 3.9+
* **Frontend:** Streamlit 1.28+
* **Databas:** SQLite 3
* **Visualisering:** Plotly 5.17+
* **Data:** Pandas 2.0+

### Dependencies
```python
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0  # För Excel-export
reportlab>=4.0.0  # För PDF-generering
```

### Filstruktur
```
esg_workspace/
├── dashboard.py              # Huvudapp (navigation)
├── modules/
│   ├── dma_matrix.py         # Modul A
│   ├── scope3_calc.py        # Modul B
│   ├── social_tracker.py     # Modul C
│   ├── governance.py         # Modul D
│   └── index_generator.py    # Modul E
├── database/
│   ├── esg_workspace.db      # SQLite
│   └── init_db.py            # Schema setup
├── utils/
│   ├── esrs_mapping.py       # ESRS logik
│   ├── emission_factors.py   # CO2e-faktorer
│   └── validators.py         # Input validation
├── data/
│   └── esrs_requirements.csv # Referensdata
└── requirements.txt
```

---

## 7. Användarflöden

### Workflow: Från noll till CSRD-rapport

1. **Steg 1: Väsentlighetsanalys (Modul A)**
   * Genomför DMA-workshop
   * Identifiera väsentliga ämnen (≥3 på någon skala)
   * Exportera resultat

2. **Steg 2: Datainsamling (Modul B-D)**
   * Om E1 väsentlig → Fyll i Scope 3 Calculator
   * Om S1 väsentlig → Importera HR-data till Social Tracker
   * Om G1 väsentlig → Inventera policys i Governance Manager

3. **Steg 3: Review & Quality Check**
   * Granska datakvalitetsflaggor (Verified vs Estimated)
   * Säkerställ att Next Review Dates är uppdaterade
   * Validera att alla väsentliga ämnen har data

4. **Steg 4: Generera rapport (Modul E)**
   * Kör Index Generator
   * Exportera ESRS Content Index
   * Skapa PDF-rapport för extern publicering

---

## 8. Key Success Metrics

### CSRD Readiness Score (KPI)
Beräknas som: `(Antal rapporterade ESRS-krav / Antal tillämpliga krav) × 100`

**Målvärden:**
* **<50%:** Grundläggande nivå (nuvarande Skills läge)
* **50-75%:** God nivå (på väg mot compliance)
* **75-90%:** Best Practice (Toyota MH-nivå)
* **>90%:** Excellent (EcoVadis Platinum)

### Data Quality Score
Beräknas för Scope 3: `(Verified data / Total data) × 100`

**Målvärde:** >60% verified data (enligt GHG Protocol best practice)

---

## 9. Risker & Mitigation

### Risk 1: Data inte tillgänglig
* **Problem:** Skill saknar spend-data för vissa kategorier
* **Lösning:** Börja med tillgängliga kategorier, flagga saknad data tydligt

### Risk 2: ESRS-krav ändras
* **Problem:** ESRS är nytt och kan justeras
* **Lösning:** Använd referenstabell (`f_ESRS_Requirements`) som lätt uppdateras

### Risk 3: Användarkomplexitet
* **Problem:** För många funktioner kan förvirra
* **Lösning:** Phased rollout enligt roadmap, tooltips och guidning i UI

---

## 10. Resurser & Referenser

### ESRS-dokumentation
* [EFRAG ESRS Set 1](https://www.efrag.org/lab6) - Officiella standarder
* ESRS 2: General Disclosures (inkl. DMA-krav)
* ESRS E1: Climate Change (Scope 1-3)
* ESRS S1: Own Workforce (HR-data)
* ESRS G1: Business Conduct (Governance)

### Emissionsfaktorer
* [DEFRA 2024](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024) - UK-faktorer
* [EPA EEIO](https://www.epa.gov/climateleadership/scope-3-inventory-guidance) - USA spend-based
* [Exiobase](https://www.exiobase.eu/) - Sektorspecifika faktorer

### GHG Protocol
* [Scope 3 Calculation Guidance](https://ghgprotocol.org/scope-3-calculation-guidance-2)
* Technical Guidance for Category 1 (Purchased Goods & Services)

---

**Version:** 1.0  
**Senast uppdaterad:** 2026-01-19  
**Status:** Implementation Ready  
**Nästa review:** Vid release av Modul