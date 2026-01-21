def calculate_purchased_goods_emissions(category: str, amount_sek: float) -> float:
    """
    Calculates CO2 emissions for purchased goods and services based on spend.
    Args:
        category (str): Category of purchased good or service (e.g., 'IT Services', 'Office Supplies', 'Consulting').
        amount_sek (float): Amount spent in SEK.
    Returns:
        float: Calculated CO2 emissions in kg.
    """
    emission_factor_kg_per_sek = 0.0 # kg CO2e per SEK

    # Placeholder emission factors (in a real scenario, these would be from EIO databases or specific supplier data)
    if category == 'IT Services':
        emission_factor_kg_per_sek = 0.0001
    elif category == 'Office Supplies':
        emission_factor_kg_per_sek = 0.0005
    elif category == 'Consulting':
        emission_factor_kg_per_sek = 0.00005
    else:
        print(f"Warning: Unknown purchased goods category '{category}'. Emissions cannot be calculated.")
        return 0.0
    
    return amount_sek * emission_factor_kg_per_sek
