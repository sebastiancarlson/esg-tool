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
    Generates a CSRD-compliant Excel report with Scope 1, 2, and 3 data.
    Returns:
        BytesIO: The Excel file in memory.
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    conn = get_db_connection()
    
    try:
        # --- Scope 1 Data ---
        try:
            scope1_df = pd.read_sql("SELECT * FROM f_Drivmedel", conn)
        except Exception:
            scope1_df = pd.DataFrame(columns=["datum", "volym_liter", "drivmedelstyp", "co2_kg"])
            
        # --- Scope 2 Data ---
        try:
            scope2_df = pd.read_sql("SELECT * FROM elforbrukning", conn) 
        except Exception:
            scope2_df = pd.DataFrame(columns=["datum", "kWh", "kostnad", "co2_kg"])

        # --- Scope 3 Data (Detailed) ---
        # Initialize Scope 3 specific dataframes
        try:
            scope3_bus_travel_df = pd.read_sql("SELECT * FROM f_Scope3_BusinessTravel", conn)
        except Exception:
            scope3_bus_travel_df = pd.DataFrame(columns=["date", "travel_type", "distance_km", "fuel_type", "class_type", "co2_kg"])

        try:
            scope3_waste_df = pd.read_sql("SELECT * FROM f_Scope3_Waste", conn)
        except Exception:
            scope3_waste_df = pd.DataFrame(columns=["date", "waste_type", "weight_kg", "disposal_method", "co2_kg"])

        try:
            scope3_purchased_goods_df = pd.read_sql("SELECT * FROM f_Scope3_PurchasedGoodsServices", conn)
        except Exception:
            scope3_purchased_goods_df = pd.DataFrame(columns=["date", "category", "amount_sek", "emission_factor_kg_per_sek", "co2_kg"])

        # Summing up new Scope 3 categories
        total_scope3_bus_travel = scope3_bus_travel_df["co2_kg"].sum() if not scope3_bus_travel_df.empty else 0
        total_scope3_waste = scope3_waste_df["co2_kg"].sum() if not scope3_waste_df.empty else 0
        total_scope3_purchased_goods = scope3_purchased_goods_df["co2_kg"].sum() if not scope3_purchased_goods_df.empty else 0

        # Total Scope 3 emissions
        total_scope3 = total_scope3_bus_travel + total_scope3_waste + total_scope3_purchased_goods

        # --- Summary Sheet ---
        summary_data = {
            "Scope": ["Scope 1", "Scope 2", "Scope 3"],
            "Total CO2e (kg)": [
                scope1_df["co2_kg"].sum() if not scope1_df.empty else 0,
                scope2_df["co2_kg"].sum() if not scope2_df.empty else 0,
                total_scope3
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Write to Excel
        summary_df.to_excel(writer, sheet_name='CSRD Summary', index=False)
        scope1_df.to_excel(writer, sheet_name='Scope 1 - Fuel', index=False)
        scope2_df.to_excel(writer, sheet_name='Scope 2 - Energy', index=False)
        
        # Add detailed Scope 3 sheets
        scope3_bus_travel_df.to_excel(writer, sheet_name='Scope 3 - Business Travel', index=False)
        scope3_waste_df.to_excel(writer, sheet_name='Scope 3 - Waste', index=False)
        scope3_purchased_goods_df.to_excel(writer, sheet_name='Scope 3 - Purchased Goods', index=False)
        
        # Add metadata/info
        workbook = writer.book
        worksheet = writer.sheets['CSRD Summary']
        worksheet.write(0, 3, "Report generated via ESG Tool")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        # Create an error sheet
        pd.DataFrame({"Error": [str(e)]}).to_excel(writer, sheet_name='Error')
    finally:
        conn.close()
        
    writer.close()
    output.seek(0)
    return output

def generate_pdf_summary(summary_df: pd.DataFrame) -> BytesIO:
    """
    Generates a PDF summary of the CSRD report.
    Args:
        summary_df (pd.DataFrame): The summary DataFrame containing Scope data.
    Returns:
        BytesIO: The PDF file in memory.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="CSRD Report Summary", ln=True, align="C")
    pdf.ln(10)

    # Add table headers
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(80, 10, "Scope", 1)
    pdf.cell(80, 10, "Total CO2e (kg)", 1, ln=True)
    pdf.set_font("Arial", size=10)

    # Add table data
    for index, row in summary_df.iterrows():
        pdf.cell(80, 10, str(row["Scope"]), 1)
        pdf.cell(80, 10, f"{row["Total CO2e (kg)"]:.2f}", 1, ln=True)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output
