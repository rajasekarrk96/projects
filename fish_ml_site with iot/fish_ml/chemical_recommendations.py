# Chemical recommendations for different water quality conditions

# Optimal water parameters for different fish species
fish_parameters = {
    'Snakehead': {'ph': (6.5, 7.5), 'tempC': (25, 32), 'turbidity': (150, 300)},
    'Silver Carp': {'ph': (6.5, 8.5), 'tempC': (20, 28), 'turbidity': (150, 300)},
    'Mrigal': {'ph': (6.5, 8.5), 'tempC': (24, 30), 'turbidity': (150, 300)},
    'Tilapia': {'ph': (6.0, 8.0), 'tempC': (24, 32), 'turbidity': (150, 300)},
    'Rohu': {'ph': (6.5, 8.5), 'tempC': (20, 30), 'turbidity': (150, 300)},
    'Common Carp': {'ph': (6.5, 8.5), 'tempC': (20, 28), 'turbidity': (150, 300)},
    'Grass Carp': {'ph': (6.5, 8.5), 'tempC': (20, 30), 'turbidity': (150, 300)},
    'Bighead Carp': {'ph': (6.5, 8.5), 'tempC': (20, 28), 'turbidity': (150, 300)},
    'Pangasius': {'ph': (6.0, 8.0), 'tempC': (22, 32), 'turbidity': (150, 300)},
    'Catfish': {'ph': (6.0, 8.0), 'tempC': (24, 30), 'turbidity': (150, 300)}
}

# Chemical treatments for different water quality issues
chemical_treatments = {
    'high_ph': {
        'chemicals': ['Phosphoric acid', 'Citric acid'],
        'instructions': 'Add acid gradually while monitoring pH levels. Test water every hour.'
    },
    'low_ph': {
        'chemicals': ['Agricultural lime', 'Sodium bicarbonate'],
        'instructions': 'Add lime or sodium bicarbonate gradually. Monitor pH changes every 2 hours.'
    },
    'high_temp': {
        'chemicals': None,
        'instructions': 'Use aerators to increase oxygen levels. Consider adding shade or increasing water depth.'
    },
    'low_temp': {
        'chemicals': None,
        'instructions': 'Use water heaters if available. Ensure proper insulation of pond.'
    },
    'high_turbidity': {
        'chemicals': ['Aluminum sulfate (Alum)', 'Gypsum'],
        'instructions': 'Apply recommended flocculant carefully. Monitor fish behavior after application.'
    }
}

def get_fish_parameters(fish_species):
    """Get optimal parameters for a specific fish species."""
    return fish_parameters.get(fish_species, None)

def get_chemical_recommendations(fish_species, current_params):
    """Get chemical recommendations based on current water parameters."""
    recommendations = []
    optimal = fish_parameters.get(fish_species)
    
    if not optimal:
        return [{'issue': 'Unknown fish species', 'treatment': None}]
    
    # Check pH with specific ranges for each fish species
    if current_params['ph'] > optimal['ph'][1]:
        ph_diff = current_params['ph'] - optimal['ph'][1]
        recommendations.append({
            'issue': f'High pH for {fish_species} (Current: {current_params["ph"]:.1f}, Optimal range: {optimal["ph"][0]:.1f}-{optimal["ph"][1]:.1f})',
            'treatment': {
                'chemicals': chemical_treatments['high_ph']['chemicals'],
                'instructions': f'For {fish_species}, pH is {ph_diff:.1f} units too high. {chemical_treatments["high_ph"]["instructions"]} {fish_species} prefers slightly {"acidic" if optimal["ph"][1] < 7.0 else "alkaline"} water.'
            }
        })
    elif current_params['ph'] < optimal['ph'][0]:
        ph_diff = optimal['ph'][0] - current_params['ph']
        recommendations.append({
            'issue': f'Low pH for {fish_species} (Current: {current_params["ph"]:.1f}, Optimal range: {optimal["ph"][0]:.1f}-{optimal["ph"][1]:.1f})',
            'treatment': {
                'chemicals': chemical_treatments['low_ph']['chemicals'],
                'instructions': f'For {fish_species}, pH is {ph_diff:.1f} units too low. {chemical_treatments["low_ph"]["instructions"]} {fish_species} prefers slightly {"acidic" if optimal["ph"][1] < 7.0 else "alkaline"} water.'
            }
        })
    
    # Check temperature with specific ranges for each fish species
    if current_params['tempC'] > optimal['tempC'][1]:
        temp_diff = current_params['tempC'] - optimal['tempC'][1]
        recommendations.append({
            'issue': f'High temperature for {fish_species} (Current: {current_params["tempC"]}°C, Optimal range: {optimal["tempC"][0]}-{optimal["tempC"][1]}°C)',
            'treatment': {
                'chemicals': chemical_treatments['high_temp']['chemicals'],
                'instructions': f'For {fish_species}, temperature is {temp_diff:.1f}°C too high. {chemical_treatments["high_temp"]["instructions"]} {fish_species} prefers cooler water between {optimal["tempC"][0]}-{optimal["tempC"][1]}°C.'
            }
        })
    elif current_params['tempC'] < optimal['tempC'][0]:
        temp_diff = optimal['tempC'][0] - current_params['tempC']
        recommendations.append({
            'issue': f'Low temperature for {fish_species} (Current: {current_params["tempC"]}°C, Optimal range: {optimal["tempC"][0]}-{optimal["tempC"][1]}°C)',
            'treatment': {
                'chemicals': chemical_treatments['low_temp']['chemicals'],
                'instructions': f'For {fish_species}, temperature is {temp_diff:.1f}°C too low. {chemical_treatments["low_temp"]["instructions"]} {fish_species} prefers warmer water between {optimal["tempC"][0]}-{optimal["tempC"][1]}°C.'
            }
        })
    
    # Check turbidity with specific ranges for each fish species
    if current_params['turbidity'] > optimal['turbidity'][1]:
        turbidity_diff = current_params['turbidity'] - optimal['turbidity'][1]
        recommendations.append({
            'issue': f'High turbidity for {fish_species} (Current: {current_params["turbidity"]}, Optimal range: {optimal["turbidity"][0]}-{optimal["turbidity"][1]})',
            'treatment': {
                'chemicals': chemical_treatments['high_turbidity']['chemicals'],
                'instructions': f'For {fish_species}, turbidity is {turbidity_diff:.1f} units too high. {chemical_treatments["high_turbidity"]["instructions"]} {fish_species} prefers clearer water with turbidity between {optimal["turbidity"][0]}-{optimal["turbidity"][1]} units.'
            }
        })
    
    return recommendations