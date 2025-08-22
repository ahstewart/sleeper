import requests
import models
import pdb

def update_player_json(api_endpoint, sport, filename="players.json"):
    response = requests.get(f"{api_endpoint}/players/{sport}")
    if response.status_code == 200:
        players = response.json()
        with open(filename, "w+") as f:
            import json
            json.dump(players, f, indent=4)
        print(f"Player data updated in {filename}")
    else:
        raise Exception(f"Error fetching players: {response.status_code}")

def fetch_all_players(api_endpoint, sport, filename="players.json"):
    # Function to fetch player data
    # First try to read from local file
    try:
        with open(filename, "r") as f:
            import json
            players = json.load(f)
            print(f"Loaded players from {filename}")
    except FileNotFoundError:
        print(f"{filename} not found, fetching from API")
        update_player_json(api_endpoint, sport, filename)
        with open(filename, "r") as f:
            import json
            players = json.load(f)
    players = models.AllPlayers.from_sleeper_json(players)
    return players

def fetch_all_teams(api_endpoint, league_id):
    # Function to fetch all teams from the external API
    response = requests.get(f"{api_endpoint}/league/{league_id}/rosters")
    if response.status_code == 200:
        all_teams = models.AllTeams.from_sleeper_json(response.json())
        return all_teams
    else:
        raise Exception(f"Error fetching all teams: {response.status_code}")
    
def fetch_all_users(api_endpoint, league_id):
    # Function to fetch users from the external API
    response = requests.get(f"{api_endpoint}/league/{league_id}/users")
    if response.status_code == 200:
        all_users = models.AllUsers.from_sleeper_json(response.json())
        return all_users
    else:
        raise Exception(f"Error fetching all users: {response.status_code}")
    
def fetch_all_drafts(api_endpoint, league_id):
    # Function to fetch all drafts from the external API
    response = requests.get(f"{api_endpoint}/league/{league_id}/drafts")
    if response.status_code == 200:
        all_drafts = models.AllDrafts.from_sleeper_json(response.json())
        return all_drafts
    else:
        raise Exception(f"Error fetching all drafts: {response.status_code}")
    
def fetch_draft_info(api_endpoint, draft_id):
    # Function to fetch live draft information from the external API
    response = requests.get(f"{api_endpoint}/draft/{draft_id}")
    if response.status_code == 200:
        draft_info = models.Draft.from_sleeper_json(response.json())
        return draft_info
    else:
        raise Exception(f"Error fetching draft info: {response.status_code}")

def fetch_draft_picks(api_endpoint, draft_id):
    # Function to fetch live draft picks from the external API
    response = requests.get(f"{api_endpoint}/draft/{draft_id}/picks")
    if response.status_code == 200:
        draft_picks = models.AllDraftPicks.from_sleeper_json(response.json())
        return draft_picks
    else:
        raise Exception(f"Error fetching draft picks: {response.status_code}")
    
def fetch_all_player_projections(api_endpoint, sport, season, season_type):
    # Function to fetch all player projections from the external API
    print(f"Fetching all player projections using URL: {api_endpoint}/projections/{sport}/{season}?season_type={season_type}&order_by=pts_std")
    response = requests.get(f"{api_endpoint}/projections/{sport}/{season}?season_type={season_type}&order_by=pts_std")
    if response.status_code == 200:
        all_projections = models.AllStats.from_sleeper_json(response.json())
        return all_projections
    else:
        raise Exception(f"Error fetching all players' projections: {response.status_code}")
    
def fetch_player_projections_by_pos(api_endpoint, sport, season, season_type, position):
    # Function to fetch player projections for a certain position from the external API
    response = requests.get(f"{api_endpoint}/projections/{sport}/{season}?season_type={season_type}&position={position}&order_by=pts_std")
    if response.status_code == 200:
        projections_by_pos = models.AllStats.from_sleeper_json(response.json())
        return projections_by_pos
    else:
        raise Exception(f"Error fetching {position} players' projections: {response.status_code}")
    
def fetch_league(api_endpoint, league_id):
    # Function to fetch league information from the external API
    response = requests.get(f"{api_endpoint}/league/{league_id}")
    if response.status_code == 200:
        league = models.League.from_sleeper_json(response.json())
        return league
    else:
        raise Exception(f"Error fetching league info: {response.status_code}")
    
def fetch_all_players_with_projections(api_endpoint, stats_endpoint, league_id, season, season_type, sport):
    # Grab scoring settings for the league
    league = fetch_league(api_endpoint, league_id)
    scoring_settings = league.scoring_settings
    # Grab all players
    all_players = fetch_all_players(api_endpoint, sport)
    # Grab season's player projections
    all_projections = fetch_all_player_projections(stats_endpoint, sport, season, season_type)
    # Apply scoring setting to each player's projection
    print(f"Applying scoring settings for league {league_id}, season {season}, type {season_type}")
    for player_id in all_projections.profiles:
        proj = 0
        for stat in all_projections.profiles[player_id].raw["stats"]:
            try:
                proj += all_projections.profiles[player_id].raw["stats"][stat] * scoring_settings[stat]
            except KeyError:
                pass
        try:
            all_players.players[player_id].update_projection(proj)
        except KeyError:
            pass
    print("Scoring settings applied successfully.")
    return all_players


if __name__ == "__main__":
    import config
    configs = config.Config()
    try:
        players = fetch_all_players_with_projections(configs.API_ENDPOINT, configs.STATS_ENDPOINT, configs.LEAGUE_ID, configs.SEASON, configs.SEASON_TYPE, configs.SPORT)
        
    except Exception as e:
        print(e)

    breakpoint()

    print(players)