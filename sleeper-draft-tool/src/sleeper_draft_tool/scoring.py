import fetchers
from tqdm import tqdm
import pdb



def calculate_player_score(player, scoring_settings):
    # Calculate the score for a player based on their projection and scoring settings
    base_score = player['projection']
    adjusted_score = apply_scoring_settings(base_score, scoring_settings)
    return adjusted_score

def calculate_team_score(team_players, scoring_settings):
    # Calculate the total score for a team based on its players' projections
    total_score = sum(calculate_player_score(player, scoring_settings) for player in team_players)
    return total_score

def get_positional_standard_deviation(players):
    # Calculate the standard deviation of player projections for a specific position
    import statistics
    projections = [player['projection'] for player in players]
    if len(projections) > 1:
        return statistics.stdev(projections)
    return 0.0


if __name__ == "__main__":
    apply_scoring_settings(1220874215918407680, 2025, "regular")