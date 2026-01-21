# Specification: CSRD Report Generation Module

## Goal
Implement a module that generates CSRD-compliant reports (Excel/PDF) based on calculated emission data.

## Features
1.  **Data Ingestion:** Read aggregated CO2 data (Scope 1, 2, 3) from the internal database (SQLite) or calculated dataframes.
2.  **CSRD Template:** Populate a standard CSRD reporting structure (ESRS E1 Climate Change).
3.  **Export:**
    -   Generate an Excel file with detailed data tables.
    -   (Optional for MVP) Generate a PDF summary.

## Tech Stack
-   Python
-   Pandas (for data handling)
-   OpenPyXL (for Excel export)
-   Streamlit (for UI trigger and download)
