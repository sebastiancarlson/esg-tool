def calculate_waste_emissions(waste_type: str, weight_kg: float, disposal_method: str) -> float:
    """
    Calculates CO2 emissions for waste generated.
    Args:
        waste_type (str): Type of waste (e.g., 'General', 'Food', 'Paper/Cardboard', 'Plastics').
        weight_kg (float): Weight of waste in kilograms.
        disposal_method (str): Method of disposal (e.g., 'Landfill', 'Recycled', 'Incinerated').
    Returns:
        float: Calculated CO2 emissions in kg.
    """
    emission_factor = 0.0 # kg CO2e per kg of waste

    # Placeholder emission factors (in a real scenario, these would be from a reliable source)
    # Factors can vary significantly by waste type and disposal method

    if disposal_method == 'Landfill':
        if waste_type == 'General':
            emission_factor = 0.25 # Example: kg CO2e per kg general waste to landfill
        elif waste_type == 'Food':
            emission_factor = 1.0 # Example: higher due to methane
        elif waste_type == 'Plastics':
            emission_factor = 1.5 # Example: higher for plastics due to embedded emissions
        else:
            emission_factor = 0.25 # Default for other landfill waste
    elif disposal_method == 'Recycled':
        # Often involves avoided emissions (negative factor), but for simplicity, 
        # using a small positive for process emissions or zero for net effect.
        if waste_type == 'Paper/Cardboard':
            emission_factor = 0.1 # Example: small process emissions
        elif waste_type == 'Plastics':
            emission_factor = 0.3 # Example: some energy for recycling
        else:
            emission_factor = 0.05 # Default for other recycled waste
    elif disposal_method == 'Incinerated':
        if waste_type == 'General':
            emission_factor = 0.15 # Example: kg CO2e per kg general waste incinerated
        else:
            emission_factor = 0.15 # Default for other incinerated waste
    else:
        print(f"Warning: Unknown disposal method '{disposal_method}'. Emissions cannot be calculated.")
        return 0.0
    
    return weight_kg * emission_factor
