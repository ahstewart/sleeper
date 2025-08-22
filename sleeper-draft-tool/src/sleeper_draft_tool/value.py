def calculate_raw_value(player_projection, team_projection):
    return player_projection / team_projection

def calculate_adjusted_value(raw_value, available_roster_spots, available_money):
    return raw_value * (available_roster_spots / available_money)

def calculate_value_over_replacement(player_value, replacement_value):
    return player_value - replacement_value

def calculate_positional_standard_deviation(player_values):
    mean_value = sum(player_values) / len(player_values)
    variance = sum((x - mean_value) ** 2 for x in player_values) / len(player_values)
    return variance ** 0.5

def get_player_value(player, team_projection, available_roster_spots, available_money, replacement_value):
    raw_value = calculate_raw_value(player['projection'], team_projection)
    adjusted_value = calculate_adjusted_value(raw_value, available_roster_spots, available_money)
    value_over_replacement = calculate_value_over_replacement(adjusted_value, replacement_value)
    
    return {
        'raw_value': raw_value,
        'adjusted_value': adjusted_value,
        'value_over_replacement': value_over_replacement
    }