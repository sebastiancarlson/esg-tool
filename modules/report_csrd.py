import pandas as pd
import sqlite3
import os
from io import BytesIO
from fpdf import FPDF

# Import new Scope 3 modules
from modules import scope3_travel
from modules import scope3_waste
from modules import scope3_purchased_goods

def get_db_connection(db_path="database/esg_index.db"):
    """Establish connection to the SQLite database."""
    # Ensure directory exists if we are running from root
    if not os.path.exists(db_path):
        # Fallback logic or error handling
        # Try finding it relative to current file if needed
        base_dir = os.path.dirname(os.path.dirname(__file__))
        alt_path = os.path.join(base_dir, "database", "esg_index.db")
        if os.path.exists(alt_path):
            return sqlite3.connect(alt_path)
    return sqlite3.connect(db_path)

def generate_csrd_report() -> BytesIO:
    """
    Generates a CSRD-compliant Excel report with Scope 1, 2, 3, Water, and Waste detailed data.
    Returns:
        BytesIO: The Excel file in memory.
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    conn = get_db_connection()
    
    try:
        # --- Scope 1 & 2 ---
        try: scope1_df = pd.read_sql("SELECT * FROM f_Drivmedel", conn)
        except Exception: scope1_df = pd.DataFrame(columns=["co2_kg"])
            
        try: scope2_df = pd.read_sql("SELECT * FROM f_Energi", conn) 
        except Exception: scope2_df = pd.DataFrame(columns=["co2_kg"])

        # --- Scope 3 Data ---
        try: scope3_bus_travel_df = pd.read_sql("SELECT * FROM f_Scope3_BusinessTravel", conn)
        except Exception: scope3_bus_travel_df = pd.DataFrame(columns=["co2_kg"])

        try: scope3_purchased_goods_df = pd.read_sql("SELECT * FROM f_Scope3_PurchasedGoodsServices", conn)
        except Exception: scope3_purchased_goods_df = pd.DataFrame(columns=["co2_kg"])
            
        # --- New Environmental Modules ---
        try: water_df = pd.read_sql("SELECT * FROM f_Water_Data", conn)
        except Exception: water_df = pd.DataFrame()
            
        try: waste_detailed_df = pd.read_sql("SELECT * FROM f_Waste_Detailed", conn)
        except Exception: waste_detailed_df = pd.DataFrame()
        
        # Legacy Waste (for backward compatibility if needed)
        try: scope3_waste_df = pd.read_sql("SELECT * FROM f_Scope3_Waste", conn)
        except Exception: scope3_waste_df = pd.DataFrame(columns=["co2_kg"])

        # Totals
        total_scope3 = (
            scope3_bus_travel_df["co2_kg"].sum() +
            scope3_purchased_goods_df["co2_kg"].sum() +
            scope3_waste_df["co2_kg"].sum() # Include legacy waste emission calc if exists
        )

        # --- Summary Sheet ---
        summary_data = {
            "Category": ["Scope 1 (Direct)", "Scope 2 (Energy)", "Scope 3 (Value Chain)", "Total Water Consumption (m3)", "Total Waste (kg)"],
            "Value": [
                scope1_df["co2_kg"].sum(),
                scope2_df.get("scope2_market_based_kg", scope2_df.get("co2_kg", pd.Series([0]))).sum(), # Handle schema variations
                total_scope3,
                water_df["consumption_m3"].sum() if not water_df.empty else 0,
                waste_detailed_df["weight_kg"].sum() if not waste_detailed_df.empty else 0
            ],
            "Unit": ["kg CO2e", "kg CO2e", "kg CO2e", "m3", "kg"]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Write to Excel
        summary_df.to_excel(writer, sheet_name='CSRD Summary', index=False)
        scope1_df.to_excel(writer, sheet_name='Scope 1 - Fuel', index=False)
        scope2_df.to_excel(writer, sheet_name='Scope 2 - Energy', index=False)
        scope3_bus_travel_df.to_excel(writer, sheet_name='Scope 3 - Travel', index=False)
        scope3_purchased_goods_df.to_excel(writer, sheet_name='Scope 3 - Purchases', index=False)
        water_df.to_excel(writer, sheet_name='Env - Water (E3)', index=False)
        waste_detailed_df.to_excel(writer, sheet_name='Env - Waste (E5)', index=False)
        
    except Exception as e:
        print(f"Error generating report: {e}")
        pd.DataFrame({"Error": [str(e)]}).to_excel(writer, sheet_name='Error')
    finally:
        conn.close()
        
    writer.close()
    output.seek(0)
    return output

def generate_pdf_summary(summary_df: pd.DataFrame, scope3_details: dict = None) -> BytesIO:
    """
    Generates a PDF summary of the CSRD report.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="CSRD Report Summary", ln=True, align="C")
    pdf.ln(10)

    # --- Main Scopes Table ---
    pdf.set_font("Arial", style='B', size=11)
    pdf.cell(200, 10, "Environmental Key Metrics", ln=True)
    
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(100, 10, "Metric", 1)
    pdf.cell(50, 10, "Value", 1)
    pdf.cell(30, 10, "Unit", 1, ln=True)
    
    pdf.set_font("Arial", size=10)
    # Using the new summary structure if passed, or default
    if "Category" in summary_df.columns:
         for index, row in summary_df.iterrows():
            pdf.cell(100, 10, str(row["Category"]), 1)
            pdf.cell(50, 10, f"{row['Value']:.2f}", 1)
            pdf.cell(30, 10, str(row['Unit']), 1, ln=True)
    else:
        # Fallback for old dataframe structure
        for index, row in summary_df.iterrows():
            pdf.cell(100, 10, str(row["Scope"]), 1)
            pdf.cell(50, 10, f"{row['Total CO2e (kg)']:.2f}", 1)
            pdf.cell(30, 10, "kg CO2e", 1, ln=True)

    # --- Scope 3 Breakdown ---
    if scope3_details:
        pdf.ln(10)
        pdf.set_font("Arial", style='B', size=11)
        pdf.cell(200, 10, "Scope 3 Breakdown", ln=True)
        
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(100, 10, "Category", 1)
        pdf.cell(50, 10, "Total CO2e (kg)", 1, ln=True)
        
        pdf.set_font("Arial", size=10)
        for category, value in scope3_details.items():
            pdf.cell(100, 10, str(category), 1)
            pdf.cell(50, 10, f"{value:.2f}", 1, ln=True)

    pdf.ln(20)
    pdf.set_font("Arial", style='I', size=8)
    pdf.cell(200, 10, txt="Generated via ESG Tool - Strategic Sustainability Management", ln=True, align="C")

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output