# Implementation Plan: Comprehensive Scope 3 Data Collection & Calculation

This plan outlines the steps to implement expanded Scope 3 data collection and calculation.

- [ ] Task: Define detailed data points and emission factors for selected Scope 3 categories
    - [ ] Sub-task: Research emission factors for Business Travel (e.g., air, rail, car)
    - [ ] Sub-task: Research emission factors for Waste Generated (e.g., landfill, recycling)
    - [ ] Sub-task: Research emission factors for a few key Purchased Goods & Services categories
- [ ] Task: Update database schema for new Scope 3 data
    - [ ] Sub-task: Add tables/columns for Business Travel data
    - [ ] Sub-task: Add tables/columns for Waste data
    - [ ] Sub-task: Add tables/columns for Purchased Goods & Services data
- [ ] Task: Implement Python calculation logic for new Scope 3 categories
    - [ ] Sub-task: Create `calculate_business_travel_emissions` function
    - [ ] Sub-task: Create `calculate_waste_emissions` function
    - [ ] Sub-task: Create `calculate_purchased_goods_emissions` function
- [ ] Task: Develop initial data entry UI for new Scope 3 categories
    - [ ] Sub-task: Add Business Travel input form to `dashboard.py`
    - [ ] Sub-task: Add Waste input form to `dashboard.py`
    - [ ] Sub-task: Add Purchased Goods & Services input form to `dashboard.py`
- [ ] Task: Integrate new Scope 3 calculations into `report_csrd.py` and overall summary
    - [ ] Sub-task: Update `generate_csrd_report` to include new Scope 3 data
    - [ ] Sub-task: Update `generate_pdf_summary` to reflect new Scope 3 totals