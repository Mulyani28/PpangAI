import pandas as pd
import numpy as np

def generate_transport_recommendations(transport_data):
    """
    Generate recommendations for reducing transport emissions.
    
    Args:
        transport_data (DataFrame): Transport emissions data
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    if transport_data.empty:
        # Default recommendations if no data
        return [
            "Consider using public transportation instead of driving when possible.",
            "Try carpooling with colleagues or neighbors to reduce per-person emissions.",
            "Look into cycling or walking for short trips to eliminate emissions and improve health.",
            "If available, consider electric or hybrid vehicles for your next car purchase."
        ]
    
    # Analyze transport types
    transport_types = transport_data.groupby('subcategory')['emission_kg'].sum().sort_values(ascending=False)
    
    # High car usage recommendations
    if 'Car' in transport_types.index and transport_types['Car'] > 0:
        car_emissions = transport_types['Car']
        recommendations.append(
            f"Your car travel contributes {car_emissions:.2f} kg CO2e. Consider carpooling, "
            "using public transport, or combining trips to reduce these emissions."
        )
        
        # Check if there's significant car usage
        if car_emissions > 50:
            recommendations.append(
                "Your car emissions are significant. Consider switching to a more fuel-efficient "
                "vehicle or an electric car for your next purchase."
            )
    
    # Air travel recommendations
    if 'Plane' in transport_types.index and transport_types['Plane'] > 0:
        plane_emissions = transport_types['Plane']
        recommendations.append(
            f"Air travel contributes {plane_emissions:.2f} kg CO2e to your footprint. "
            "Consider videoconferencing instead of flying for business when possible, "
            "and choose direct flights which typically have lower emissions."
        )
    
    # Public transport encouragement
    if ('Bus' not in transport_types.index or transport_types.get('Bus', 0) < 10) and \
       ('Train' not in transport_types.index or transport_types.get('Train', 0) < 10):
        recommendations.append(
            "You show limited use of public transportation. Buses and trains generally "
            "have lower per-person emissions than cars. Try incorporating public transit "
            "into your regular travel routine."
        )
    
    # Cycling/walking encouragement
    if ('Bike' not in transport_types.index or transport_types.get('Bike', 0) == 0) and \
       ('Walking' not in transport_types.index or transport_types.get('Walking', 0) == 0):
        recommendations.append(
            "Consider walking or cycling for short trips. These zero-emission options "
            "are not only good for the environment but also for your health."
        )
    
    # Add general recommendations if we don't have enough specific ones
    if len(recommendations) < 3:
        general_recommendations = [
            "Plan and combine errands to reduce the number of trips you take.",
            "Regular vehicle maintenance ensures optimal fuel efficiency and lower emissions.",
            "Consider working from home one or more days a week if your job allows it.",
            "When renting cars, choose fuel-efficient or electric models."
        ]
        recommendations.extend(general_recommendations[:3 - len(recommendations)])
    
    return recommendations[:4]  # Return at most 4 recommendations

def generate_energy_recommendations(energy_data):
    """
    Generate recommendations for reducing energy emissions.
    
    Args:
        energy_data (DataFrame): Energy emissions data
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    if energy_data.empty:
        # Default recommendations if no data
        return [
            "Switch to LED light bulbs, which use up to 80% less energy than traditional bulbs.",
            "Unplug electronics when not in use to avoid phantom energy consumption.",
            "Consider a home energy audit to identify opportunities for improving efficiency.",
            "Look into renewable energy options such as solar panels or green energy providers."
        ]
    
    # Analyze energy types
    energy_types = energy_data.groupby('subcategory')['emission_kg'].sum().sort_values(ascending=False)
    
    # Electricity recommendations
    if 'Electricity' in energy_types.index and energy_types['Electricity'] > 0:
        elec_emissions = energy_types['Electricity']
        recommendations.append(
            f"Your electricity usage contributes {elec_emissions:.2f} kg CO2e. Install LED bulbs, "
            "use smart power strips, and turn off lights and appliances when not in use."
        )
        
        if elec_emissions > 100:
            recommendations.append(
                "Consider switching to a renewable energy provider or installing solar panels "
                "to significantly reduce your electricity emissions."
            )
    
    # Heating recommendations
    if 'Natural Gas' in energy_types.index or 'Heating Oil' in energy_types.index:
        heating_emissions = energy_types.get('Natural Gas', 0) + energy_types.get('Heating Oil', 0)
        recommendations.append(
            f"Your heating contributes {heating_emissions:.2f} kg CO2e. Improve home insulation, "
            "use a programmable thermostat, and consider a more efficient heating system."
        )
    
    # Renewable energy encouragement
    if 'Renewable' not in energy_types.index or energy_types.get('Renewable', 0) < 5:
        recommendations.append(
            "You show limited use of renewable energy. Consider installing solar panels, "
            "switching to a green energy provider, or participating in community solar programs."
        )
    
    # Add general recommendations if we don't have enough specific ones
    if len(recommendations) < 3:
        general_recommendations = [
            "Wash clothes in cold water to save energy used for heating.",
            "Air-dry clothes instead of using a dryer when possible.",
            "Ensure your home is well-insulated to prevent energy waste.",
            "Use natural light when possible and turn off lights in unoccupied rooms."
        ]
        recommendations.extend(general_recommendations[:3 - len(recommendations)])
    
    return recommendations[:4]  # Return at most 4 recommendations

def generate_waste_recommendations(waste_data):
    """
    Generate recommendations for reducing waste emissions.
    
    Args:
        waste_data (DataFrame): Waste data
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    if waste_data.empty:
        # Default recommendations if no data
        return [
            "Start composting food scraps to reduce organic waste going to landfills.",
            "Use reusable shopping bags, water bottles, and food containers to reduce plastic waste.",
            "Buy products with minimal packaging or packaging that can be recycled.",
            "Repair items when possible instead of replacing them to reduce waste."
        ]
    
    # Analyze waste types and disposal methods
    waste_types = waste_data.groupby('waste_type')['weight_kg'].sum().sort_values(ascending=False)
    disposal_methods = waste_data.groupby('disposal_method')['weight_kg'].sum()
    
    total_waste = waste_data['weight_kg'].sum()
    
    # Calculate recycling rate
    recycled = disposal_methods.get('Recycled', 0)
    recycling_rate = (recycled / total_waste * 100) if total_waste > 0 else 0
    
    # Recycling recommendations
    if recycling_rate < 30:
        recommendations.append(
            f"Your recycling rate is {recycling_rate:.1f}%, which is below average. "
            "Set up clearly labeled recycling bins and learn about local recycling guidelines."
        )
    
    # Plastic waste recommendations
    if 'Plastic' in waste_types.index and waste_types['Plastic'] > 0:
        plastic_weight = waste_types['Plastic']
        plastic_percentage = (plastic_weight / total_waste * 100) if total_waste > 0 else 0
        
        if plastic_percentage > 20:
            recommendations.append(
                f"Plastic makes up {plastic_percentage:.1f}% of your waste. "
                "Reduce plastic use by choosing reusable items and products with less packaging."
            )
    
    # Organic waste recommendations
    if 'Organic' in waste_types.index:
        organic_weight = waste_types['Organic']
        organic_percentage = (organic_weight / total_waste * 100) if total_waste > 0 else 0
        
        composted = waste_data[
            (waste_data['waste_type'] == 'Organic') & 
            (waste_data['disposal_method'] == 'Composted')
        ]['weight_kg'].sum()
        
        compost_rate = (composted / organic_weight * 100) if organic_weight > 0 else 0
        
        if compost_rate < 50:
            recommendations.append(
                "Most of your organic waste isn't being composted. Start composting food scraps "
                "to reduce methane emissions from landfills and create nutrient-rich soil."
            )
    
    # Electronic waste recommendations
    if 'Electronic' in waste_types.index and waste_types['Electronic'] > 0:
        recommendations.append(
            "You've recorded electronic waste. Ensure these items are properly recycled through "
            "e-waste programs to recover valuable materials and prevent toxic substances from leaching."
        )
    
    # Landfill reduction recommendations
    landfill = disposal_methods.get('Landfill', 0)
    landfill_percentage = (landfill / total_waste * 100) if total_waste > 0 else 0
    
    if landfill_percentage > 50:
        recommendations.append(
            f"{landfill_percentage:.1f}% of your waste goes to landfill. "
            "Focus on reducing, reusing, recycling, and composting to minimize landfill waste."
        )
    
    # Add general recommendations if we don't have enough specific ones
    if len(recommendations) < 3:
        general_recommendations = [
            "Shop with waste reduction in mind by buying in bulk and choosing products with less packaging.",
            "Use reusable shopping bags, water bottles, and food containers.",
            "Donate usable items instead of throwing them away.",
            "Repair items when possible instead of replacing them."
        ]
        recommendations.extend(general_recommendations[:3 - len(recommendations)])
    
    return recommendations[:4]  # Return at most 4 recommendations

def generate_overall_recommendations(emission_data, waste_data):
    """
    Generate overall sustainability recommendations.
    
    Args:
        emission_data (DataFrame): Emissions data
        waste_data (DataFrame): Waste data
        
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    # Default recommendations if no data
    if emission_data.empty and waste_data.empty:
        return [
            "Track your daily activities to understand and reduce your carbon footprint.",
            "Replace high-emission activities with lower-impact alternatives when possible.",
            "Choose energy-efficient appliances and electronics for your home.",
            "Support sustainable businesses and products with environmentally friendly practices."
        ]
    
    # Calculate total emissions
    total_emissions = 0
    if not emission_data.empty:
        total_emissions = emission_data['emission_kg'].sum()
    
    # Generate emission-based recommendations
    if total_emissions > 0:
        # Analyze highest emission categories
        if 'category' in emission_data.columns:
            categories = emission_data.groupby('category')['emission_kg'].sum().sort_values(ascending=False)
            
            if not categories.empty:
                highest_category = categories.index[0]
                highest_emissions = categories.iloc[0]
                highest_percentage = (highest_emissions / total_emissions * 100)
                
                recommendations.append(
                    f"Your highest emissions ({highest_percentage:.1f}%) come from {highest_category}. "
                    f"Focus on reducing this category to make the biggest impact."
                )
    
    # Add food-based recommendations
    if not emission_data.empty and 'Food' in emission_data['category'].values:
        food_emissions = emission_data[emission_data['category'] == 'Food']
        
        # Check for high-impact foods
        if 'subcategory' in food_emissions.columns:
            high_impact_foods = ['Beef', 'Dairy']
            has_high_impact = any(food in food_emissions['subcategory'].values for food in high_impact_foods)
            
            if has_high_impact:
                recommendations.append(
                    "Consider reducing consumption of beef and dairy, which have high carbon footprints. "
                    "Try incorporating more plant-based meals into your diet."
                )
    
    # Add recommendations based on total footprint
    if total_emissions > 1000:
        recommendations.append(
            "Your carbon footprint is significant. Consider offsetting emissions through "
            "verified carbon offset programs while working to reduce your overall impact."
        )
    
    # Add seasonal energy recommendations
    import datetime
    current_month = datetime.datetime.now().month
    
    if 3 <= current_month <= 5:  # Spring
        recommendations.append(
            "As warmer weather approaches, use natural ventilation instead of air conditioning "
            "when possible, and consider air-drying clothes to save energy."
        )
    elif 6 <= current_month <= 8:  # Summer
        recommendations.append(
            "During hot months, use fans instead of air conditioning when comfortable, "
            "and close blinds during the day to keep your home cooler naturally."
        )
    elif 9 <= current_month <= 11:  # Fall
        recommendations.append(
            "As temperatures drop, add layers of clothing and use blankets before turning up the heat. "
            "Check your home insulation and seal any drafty areas."
        )
    else:  # Winter
        recommendations.append(
            "During cold months, keep thermostats at moderate temperatures and use programmable "
            "settings to reduce heating when you're away or sleeping."
        )
    
    # Add general sustainability recommendations
    general_recommendations = [
        "Consider planting trees or supporting reforestation projects to offset carbon emissions.",
        "Advocate for climate policies in your community and support environmental organizations.",
        "Look for sustainability certifications when shopping, such as Energy Star, LEED, or Fair Trade.",
        "Share your sustainability journey with others to spread awareness and encourage action.",
        "Regularly review your footprint data to identify new areas for improvement."
    ]
    
    # Add general recommendations to fill out the list
    recommendations.extend(general_recommendations[:5 - len(recommendations)])
    
    return recommendations[:5]  # Return at most 5 recommendations
