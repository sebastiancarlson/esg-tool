# Implementation Plan: Water & Waste Management Module

This plan outlines the steps to build the comprehensive Water (ESRS E3) and Waste (ESRS E5) module.

- [x] Task: Update Database Schema
    - [x] Sub-task: Create `f_Water_Data` table
    - [x] Sub-task: Create `f_Waste_Detailed` table (or migrate existing `f_Scope3_Waste`)
- [x] Task: Create Backend Logic (`modules/env_water.py`, `modules/env_waste.py`)
    - [x] Sub-task: Functions to add/get water data
    - [x] Sub-task: Functions to calculate water metrics (intensity, consumption)
    - [x] Sub-task: Functions to add/get detailed waste data
    - [x] Sub-task: Functions to calculate waste metrics (recycling rate, hazardous %)
- [x] Task: Implement UI in `dashboard.py`
    - [x] Sub-task: Create "Vatten" tab under "Miljö" section
    - [x] Sub-task: Update "Avfall" tab to use new detailed data model and fields (Hazardous check)
    - [x] Sub-task: Add visualizations (Water trends, Waste breakdown)
- [x] Task: Update Reporting
    - [x] Sub-task: Ensure new data points are available in Excel export
