# Förslag på framtida implementeringar - ESG Tool

Dessa punkter baseras på sessionen 2026-01-19 och syftar till att lyfta verktyget från en fungerande prototyp till en fullskalig compliance-plattform.

## 1. Data & Beräkningar (Scope 3)
- [ ] **Vikt-baserade beräkningar:** Lägg till stöd för kg/ton för t.ex. livsmedel (Nivå 2 precision) som komplement till Spend-metoden.
- [ ] **Realtids-API för avstånd:** Ersätt placeholder-logiken i `distance_api.py` med Google Maps eller OpenRouteService för exakta pendlingsberäkningar.
- [ ] **Leverantörs-portal:** En enkel landningssida där leverantörer kan ladda upp sina egna EPD:er (Environmental Product Declarations) direkt i systemet.

## 2. Automatisk Dokumentation & Export
- [ ] **Direkt OneDrive-synk:** Automatisera exporten av Excel-underlag och PDF-rapporter direkt till Jennys OneDrive istället för manuell nedladdning.
- [ ] **Stärkt PDF-motor:** Implementera en mer robust PDF-generering (t.ex. via en Docker-container för WeasyPrint eller en molntjänst) för att garantera perfekt formatering.
- [ ] **Bilagor till PDF:** Automatisk inkludering av uppladdade policydokument som bilagor i den stora CSRD-rapporten.

## 3. Revision & Spårbarhet (Audit Trail)
- [ ] **Interaktiv Drill-down:** Gör mätartalen på Översikten klickbara. Om man klickar på "Scope 3" ska man skickas till en filtrerad lista över alla underliggande transaktioner.
- [ ] **Logg-visare:** En dedikerad vy i "Revisorvy" som visar vem som ändrade vad och när (förändringshistorik).

## 4. Användarvänlighet & UI
- [ ] **Flerårs-jämförelse:** Möjlighet att se grafer som jämför 2024 mot 2025 för att visa på faktisk minskning (Trend-analys).
- [ ] **Fleranvändarstöd:** Implementera riktig RBAC (Role-Based Access Control) med olika behörigheter för t.ex. J.M. (Admin) och externa revisorer.
- [ ] **Automatiska Påminnelser:** E-postnotiser när en Policy närmar sig sitt "Next Review Date".

## 5. Compliance
- [ ] **Fullständig ESRS-mappning:** Utöka `f_ESRS_Requirements` med samtliga ~1100 datapunkter från CSRD-förordningen för en komplett Gap-analys.
