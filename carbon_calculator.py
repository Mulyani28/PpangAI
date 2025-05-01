def calculate_transport_emissions(transport_type, distance_km):
    """
    Calculate carbon emissions from transportation.
    
    Args:
        transport_type (str): Type of transportation (Car, Bus, Train, etc.)
        distance_km (float): Distance traveled in kilometers
        
    Returns:
        float: Carbon emissions in kg CO2e
    """
    # Emission factors in kg CO2e per km
    # Source: DEFRA 2021 emission factors
    emission_factors = {
        'Car': 0.17, # Average petrol car
        'Bus': 0.103,
        'Train': 0.037,
        'Plane': 0.255, # Short-haul flight, economy
        'Bike': 0,
        'Walking': 0,
        'Other': 0.15 # Default value
    }
    
    # Get the emission factor for the transport type
    factor = emission_factors.get(transport_type, emission_factors['Other'])
    
    # Calculate emissions
    emissions = distance_km * factor
    
    return emissions

def calculate_energy_emissions(energy_type, amount):
    """
    Calculate carbon emissions from energy consumption.
    
    Args:
        energy_type (str): Type of energy (Electricity, Natural Gas, etc.)
        amount (float): Amount of energy consumed
        
    Returns:
        float: Carbon emissions in kg CO2e
    """
    # Emission factors
    # Source: EPA and IEA data
    emission_factors = {
        'Electricity': 0.233, # kg CO2e per kWh (US average)
        'Natural Gas': 0.2, # kg CO2e per kWh
        'Heating Oil': 0.27, # kg CO2e per kWh
        'Renewable': 0.025, # kg CO2e per kWh (lifecycle emissions)
        'Other': 0.2 # Default value
    }
    
    # Unit conversion factors to kWh
    unit_conversions = {
        'Electricity': 1, # Already in kWh
        'Natural Gas': 10.55, # m³ to kWh
        'Heating Oil': 10.96, # liter to kWh
        'Renewable': 1, # Already in kWh
        'Other': 1 # Assume kWh
    }
    
    # Get the emission factor for the energy type
    factor = emission_factors.get(energy_type, emission_factors['Other'])
    
    # Get unit conversion factor
    conversion = unit_conversions.get(energy_type, 1)
    
    # Convert to kWh if needed and calculate emissions
    kWh_equivalent = amount * conversion
    emissions = kWh_equivalent * factor
    
    return emissions

def calculate_food_emissions(food_type, weight_kg):
    """
    Calculate carbon emissions from food consumption.
    
    Args:
        food_type (str): Type of food
        weight_kg (float): Weight in kilograms
        
    Returns:
        float: Carbon emissions in kg CO2e
    """
    # Emission factors in kg CO2e per kg of food
    # Source: Various life-cycle assessment studies
    emission_factors = {
        'Beef': 60, # High impact
        'Pork': 7,
        'Chicken': 6,
        'Fish': 5, # Average wild-caught and farmed
        'Dairy': 21, # Includes milk, cheese, etc.
        'Vegetables': 2,
        'Fruits': 1.1,
        'Processed Foods': 5.5,
        'Other': 4 # Default value
    }
    
    # Get the emission factor for the food type
    factor = emission_factors.get(food_type, emission_factors['Other'])
    
    # Calculate emissions
    emissions = weight_kg * factor
    
    return emissions

def calculate_waste_emissions(waste_type, weight_kg, disposal_method):
    """
    Calculate carbon emissions from waste generation and disposal.
    
    Args:
        waste_type (str): Type of waste
        weight_kg (float): Weight in kilograms
        disposal_method (str): Method of disposal
        
    Returns:
        float: Carbon emissions in kg CO2e
    """
    # Base emission factors by waste type in kg CO2e per kg waste
    # Source: EPA and waste management research
    base_emission_factors = {
        'Plastic': 6,
        'Paper': 3.5,
        'Glass': 0.85,
        'Metal': 4.5,
        'Organic': 1.9,
        'Electronic': 20,
        'Other': 3 # Default value
    }
    
    # Disposal method modifiers (multipliers)
    disposal_modifiers = {
        'Landfill': 1.0, # Base case
        'Recycled': 0.3, # 70% reduction
        'Composted': 0.1, # 90% reduction for compostable waste
        'Reused': 0.05, # 95% reduction
        'Incinerated': 0.8 # 20% reduction
    }
    
    # Get the base emission factor for the waste type
    base_factor = base_emission_factors.get(waste_type, base_emission_factors['Other'])
    
    # Get the disposal method modifier
    modifier = disposal_modifiers.get(disposal_method, disposal_modifiers['Landfill'])
    
    # Calculate emissions
    emissions = weight_kg * base_factor * modifier
    
    return emissions

def calculate_total_carbon_footprint(emission_data):
    """
    Calculate total carbon footprint from all emission sources.
    
    Args:
        emission_data (DataFrame): DataFrame containing emission records
        
    Returns:
        float: Total carbon emissions in kg CO2e
    """
    if emission_data.empty:
        return 0
    
    # Sum all emissions
    total_emissions = emission_data['emission_kg'].sum()
    
    return total_emissions

def calculate_average_daily_emissions(emission_data):
    """
    Calculate average daily carbon emissions.
    
    Args:
        emission_data (DataFrame): DataFrame containing emission records with dates
        
    Returns:
        float: Average daily emissions in kg CO2e
    """
    if emission_data.empty:
        return 0
    
    import pandas as pd
    
    # Convert date to datetime if not already
    emission_data = emission_data.copy()
    if not pd.api.types.is_datetime64_dtype(emission_data['date']):
        emission_data['date'] = pd.to_datetime(emission_data['date'])
    
    # Group by date and sum emissions
    daily_emissions = emission_data.groupby('date')['emission_kg'].sum()
    
    # Calculate average
    average_daily = daily_emissions.mean()
    
    return average_daily

def compare_to_average_footprint(total_emissions_kg):
    """
    Compare total emissions to average per capita emissions.
    
    Args:
        total_emissions_kg (float): Total emissions in kg CO2e
        
    Returns:
        dict: Comparison results
    """
    # Average annual per capita emissions in kg CO2e
    # Source: World Bank data (approximate)
    country_averages = {
        'World': 4800,
        'USA': 16500,
        'EU': 8600,
        'China': 7500,
        'India': 1900
    }
    
    # Convert to daily averages
    daily_averages = {country: value / 365 for country, value in country_averages.items()}
    
    # Compare to world average
    world_average = country_averages['World']
    percentage_of_world_avg = (total_emissions_kg / world_average) * 100
    
    # Find closest country
    emissions_diff = {
        country: abs(total_emissions_kg - emissions) 
        for country, emissions in country_averages.items()
    }
    closest_country = min(emissions_diff.items(), key=lambda x: x[1])[0]
    
    return {
        'world_average_kg': world_average,
        'percentage_of_world_avg': percentage_of_world_avg,
        'closest_country': closest_country,
        'country_averages': country_averages
    }
