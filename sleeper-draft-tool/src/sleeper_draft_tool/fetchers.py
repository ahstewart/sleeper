import requests
import models
import pdb

def fetch_all_players(api_endpoint, sport):
    # Function to fetch player projections from the external API
    response = requests.get(f"{api_endpoint}/players/{sport}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching all players: {response.status_code}")

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
        return response.json()
    else:
        raise Exception(f"Error fetching all drafts: {response.status_code}")
    
def fetch_draft_info(api_endpoint, draft_id):
    # Function to fetch live draft information from the external API
    response = requests.get(f"{api_endpoint}/draft/{draft_id}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching draft info: {response.status_code}")

def fetch_draft_picks(api_endpoint, draft_id):
    # Function to fetch live draft picks from the external API
    response = requests.get(f"{api_endpoint}/draft/{draft_id}/picks")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching draft picks: {response.status_code}")
    
def fetch_all_player_projections(api_endpoint, sport, season, season_type):
    # Function to fetch all player projections from the external API
    print(f"Fetching all player projections using URL: {api_endpoint}/projections/{sport}/{season}?season_type={season_type}&order_by=pts_std")
    response = requests.get(f"{api_endpoint}/projections/{sport}/{season}?season_type={season_type}&order_by=pts_std")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching all players' projections: {response.status_code}")
    
def fetch_player_projections_by_pos(api_endpoint, sport, season, season_type, position):
    # Function to fetch player projections for a certain position from the external API
    response = requests.get(f"{api_endpoint}/projections/{sport}/{season}?season_type={season_type}&position={position}&order_by=pts_std")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching {position} players' projections: {response.status_code}")



if __name__ == "__main__":
    import config
    configs = config.Config()
    try:
        players = fetch_all_player_projections(configs.STATS_ENDPOINT, configs.SPORT, configs.SEASON, configs.SEASON_TYPE)
        print("players:", players)
        
    except Exception as e:
        print(e)

    breakpoint()

    player_model = models.AllStats.from_sleeper_json(players)

    breakpoint()

    print("Player Name:", player_model.players['6462'].full_name)