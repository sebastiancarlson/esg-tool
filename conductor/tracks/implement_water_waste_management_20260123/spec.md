# Specification: Water & Waste Management Module

## 1. Overview
This module expands the ESG platform to cover detailed environmental data regarding water usage (ESRS E3) and waste management (ESRS E5). It goes beyond the basic Scope 3 waste calculation to track specific waste types, hazardous status, and water lifecycle metrics.

## 2. Goals
- **Water (ESRS E3):** Track water withdrawal, consumption, and discharge by source/destination.
- **Waste (ESRS E5):** Track waste generation by specific type (EWC codes optional but recommended), hazardous status, and treatment method (Recovery vs Disposal).
- **Compliance:** Support reporting for CSRD/ESRS E3-4 (Water) and E5-5 (Waste).

## 3. Data Model

### 3.1 Water Data (`f_Water_Data`)
| Column | Type | Description |
|or|---|---|
| `id` | INTEGER | Primary Key |
| `date` | TEXT | Date of record |
| `site_id` | INTEGER | Foreign Key to Sites (optional) |
| `withdrawal_m3` | REAL | Total water withdrawn |
| `withdrawal_source` | TEXT | Surface, Groundwater, Seawater, Third-party (Municipal) |
| `discharge_m3` | REAL | Total water discharged |
| `discharge_dest` | TEXT | Surface, Groundwater, Seawater, Third-party (Sewer) |
| `consumption_m3` | REAL | Calculated (Withdrawal - Discharge) or Measured |
| `recycled_m3` | REAL | Water recycled/reused internally |

### 3.2 Waste Data Enhancement (`f_Waste_Detailed`)
*Replacing or extending existing simple waste table.*
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary Key |
| `date` | TEXT | Date of record |
| `waste_category` | TEXT | Paper, Plastic, Metal, Chemical, Organic, Mixed |
| `is_hazardous` | INTEGER | 1 = Hazardous, 0 = Non-hazardous |
| `weight_kg` | REAL | Weight in kg |
| `treatment_method` | TEXT | Reuse, Recycling, Incineration (energy), Incineration (no energy), Landfill |
| `supplier` | TEXT | Waste management contractor |

## 4. User Interface
- **Water Tab:**
    - Input form for monthly water bills/meter readings.
    - Charts showing consumption trends and water intensity (m3 / employee or SEK).
- **Waste Tab:**
    - Enhanced input form with "Hazardous" checkbox.
    - Breakdown charts: Hazardous vs Non-Hazardous, Recycling Rate (%).

## 5. Calculations
- **Water Intensity:** Total Consumption / Revenue or FTE.
- **Recycling Rate:** (Reuse + Recycling) / Total Waste Generated.
