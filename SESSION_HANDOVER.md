# Session Handover: ESG Tool Deployment
**Datum:** 2026-01-18 -> 2026-01-19
**Status:** Under driftsättning (Deployment)

## Sammanfattning av dagsutförande
- **CLI Fixad:** `dist/esg-cli.exe` fungerar nu korrekt efter att en ny entrypoint (`run_cli.py`) skapats och byggts om med PyInstaller.
- **Dashboard Portabilitet:** För att göra appen tillgänglig för din handledare har vi valt att köra via Streamlit Cloud istället för en klumpig .exe-fil.
- **GitHub:** Appen är uppladdad till [https://github.com/sebastiancarlson/esg-tool](https://github.com/sebastiancarlson/esg-tool).
- **Struktur:** Projektet är omstrukturerat med `dashboard.py` och `modules/` i roten för enkel deploy.

## Pågående problem
- Streamlit Cloud rapporterar att den inte hittar repositoryt eller filen `dashboard.py` trots att de finns på GitHub. 
- **Trolig orsak:** Repository-synkronisering eller rättigheter (Public vs Private).

## Att göra imorgon (Checklista)
1. [ ] Kontrollera att GitHub-repot är satt till **Public** (enklast för demo).
2. [ ] Logga ut och in på `share.streamlit.io` för att tvinga en ny synk med GitHub.
3. [ ] Genomför deployment med följande inställningar:
   - **Repo:** `sebastiancarlson/esg-tool`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
4. [ ] Verifiera att PDF-generering fungerar (krav på `packages.txt`).
5. [ ] Skicka den skarpa länken till din handledare!

---
**Viktig notering:** Denna app är ett fristående projekt och är **inte** en del av Structura Systems.
