# Specification: Comprehensive Scope 3 Data Collection & Calculation

**Goal:** Expand the existing Scope 3 module to capture data for at least 3-5 high-priority Scope 3 categories and implement their calculation methodologies. This includes initial data entry forms and preparing for Microsoft 365/SharePoint integration.

**Focus Categories (examples, to be refined during implementation):**
- Business Travel (e.g., flights, trains, cars)
- Waste Generated in Operations
- Purchased Goods & Services (initial focus on a few key categories)
- Employee Commuting (further refinement)

**Key Requirements:**
- Database schema updates to store new Scope 3 data.
- Python functions for calculating emissions for each new category.
- Initial UI for data input (Streamlit, with a view towards Power Apps compatibility).
- Design Python functions to be exposed via API endpoints for future Azure Functions/Power Apps integration.
- Data schema to be compatible with Azure SQL Database.
