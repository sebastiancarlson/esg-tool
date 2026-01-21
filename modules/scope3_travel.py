def calculate_business_travel_emissions(travel_type: str, distance_km: float, fuel_type: str = None, class_type: str = 'Economy') -> float:
    """
    Calculates CO2 emissions for business travel.
    Args:
        travel_type (str): Type of travel (e.g., 'Flight-Short', 'Flight-Medium', 'Flight-Long', 'Rail', 'Car').
        distance_km (float): Distance traveled in kilometers.
        fuel_type (str, optional): Fuel type for car travel (e.g., 'Petrol', 'Diesel'). Defaults to None.
        class_type (str, optional): Class type for flights (e.g., 'Economy', 'Business'). Defaults to 'Economy'.
    Returns:
        float: Calculated CO2 emissions in kg.
    """
    emission_factor = 0.0 # kg CO2e per km

    # Placeholder emission factors (in a real scenario, these would be from a reliable source)
    if travel_type == 'Flight-Short': # < 1000 km
        emission_factor = 0.15
    elif travel_type == 'Flight-Medium': # 1000 - 3700 km
        emission_factor = 0.12
    elif travel_type == 'Flight-Long': # > 3700 km
        emission_factor = 0.10
    elif travel_type == 'Rail':
        emission_factor = 0.03
    elif travel_type == 'Car':
        # More specific factors could be used based on fuel_type, car size, etc.
        # For simplicity, using a generic factor for car.
        emission_factor = 0.18 # per vehicle-km, assumes 1 passenger for now
    else:
        print(f"Warning: Unknown travel type '{travel_type}'. Emissions cannot be calculated.")
        return 0.0
    
    # Adjust for flight class (simplified assumption)
    if travel_type.startswith('Flight'):
        if class_type == 'Business':
            emission_factor *= 1.5 # Business class often has higher per-passenger emissions due to space
        elif class_type == 'First':
            emission_factor *= 2.0 # First class even higher
    
    return distance_km * emission_factor
