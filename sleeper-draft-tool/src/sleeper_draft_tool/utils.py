def format_player_data(player):
    # Function to format player data for display
    return f"{player['name']} - {player['position']} - {player['team']}"

def validate_draft_budget(budget):
    # Function to validate the draft budget
    if budget < 0:
        raise ValueError("Draft budget cannot be negative.")
    return True

def calculate_percentage(part, whole):
    # Function to calculate the percentage of a part of a whole
    if whole == 0:
        return 0
    return (part / whole) * 100

# Additional utility functions can be added here as needed.