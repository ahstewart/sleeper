import fetchers
import pdb
from tqdm import tqdm
import numpy as np

def clean_player_data(players, league):
    # get rid of bench dudes and positions that are not relevant
    removal_list = []
    # get league positions
    league_positions = league.roster_positions
    for p in tqdm(players.players):
        #print(p)
        if ((players.players[p].projection == 0) or (players.players[p].projection is None) or (players.players[p].position not in league_positions)):
            #print(f"Removing player {p}")
            removal_list.append(p)
    print(f"Removing {len(removal_list)} players with 0 projection or irrelevant position")
    for removing in removal_list:
        players.remove_player(removing)
    print(f"Remaining players: {len(players.players)}")
    return players

def calculate_position_stats(players, league, buffer=1):
    league_positions = league.roster_positions
    total_rosters = league.total_rosters
    # Calculate median projection for each position
    position_projections = {}
    for pid in players.players:
        try:
            proj = players.players[pid].projection
            pos = players.players[pid].position
            position_projections[pos].append(proj)
        except KeyError:
            position_projections[pos] = [proj]

    position_stats = {}
    for position in position_projections:
        # only calucalte stats for number of positions available in the league plus a buffer
        num_positions = league_positions.count(position) * total_rosters + buffer
        cleaned_position_projections = position_projections[position]
        cleaned_position_projections.sort(reverse=True)
        cleaned_position_projections = cleaned_position_projections[:num_positions]
        print(cleaned_position_projections)
        position_stats[position] = {
            'mean': np.mean(cleaned_position_projections),
            'median': np.median(cleaned_position_projections),
            'std_dev': np.std(cleaned_position_projections)
        }

    return position_stats

def calculate_vorps(cleaned_players, league):
    stats = calculate_position_stats(cleaned_players, league)
    for pid in cleaned_players.players:
        player = cleaned_players.players[pid]
        pos = player.position
        if pos in stats:
            player.vorp = player.projection - stats[pos]['median']
        else:
            player.vorp = 0.0
    return cleaned_players

def calculate_teamshare(cleaned_players, league):
    stats = calculate_position_stats(cleaned_players, league)
    league_positions = league.roster_positions
    median_team_total = 0
    for position in stats:
        num_positions = league_positions.count(position)
        median_team_total += stats[position]['median'] * num_positions
    print(f"Median team total projection: {median_team_total}")
    for pid in cleaned_players.players:
        player = cleaned_players.players[pid]
        player.teamshare = player.projection / median_team_total if median_team_total > 0 else 0.0
    return cleaned_players

def calculate_stddevs(cleaned_players, league):
    stats = calculate_position_stats(cleaned_players, league)
    for pid in cleaned_players.players:
        player = cleaned_players.players[pid]
        player.stddevs = player.vorp / stats[player.position]['std_dev'] if stats[player.position]['std_dev'] > 0 else 0.0
    return cleaned_players

def calculate_raw_value(cleaned_players, league, draft_amount):
    for pid in cleaned_players.players:
        player = cleaned_players.players[pid]
        player.raw_value = player.teamshare * draft_amount
    return cleaned_players

# Additional utility functions can be added here as needed.

if __name__ == "__main__":
    import config
    configs = config.Config()
    players = fetchers.fetch_relevant_players_with_projections(configs.API_ENDPOINT, configs.STATS_ENDPOINT, configs.LEAGUE_ID, 
                                                          configs.SEASON, configs.SEASON_TYPE, configs.SPORT)
    #players = fetchers.fetch_all_players(configs.API_ENDPOINT, configs.SPORT)
    breakpoint()

    league = fetchers.fetch_league(configs.API_ENDPOINT, configs.LEAGUE_ID)
    cleaned_players = clean_player_data(players, league)
    breakpoint()
    print(f"Cleaned players: {cleaned_players.players}")

    calculate_medians(cleaned_players, league)