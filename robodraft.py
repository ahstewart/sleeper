import pandas
import requests
import csv
from tqdm import tqdm
from draft_results import getUserId, getScoringSettings
from sleeper_wrapper import Stats, Players, User, League

def getPlayerProjection(score_settings, players_stats):
    proj_dict = {}
    for player_id in players_stats:
        proj = 0
        for ps in players_stats[player_id]:
            try:
                proj += players_stats[player_id][ps] * score_settings[ps]
            except KeyError:
                pass
        proj_dict[player_id] = proj
    return proj_dict



if __name__ == "__main__":
    username = "ahstewart"
    pos = "regular"
    season = 2024

    user_id = getUserId(username)
    user = User(user_id)
    user_draft_details = user.get_all_drafts("nfl", season)
    draft_id = user_draft_details[0]['draft_id']
    league_id = user_draft_details[0]['league_id']
    scoring_settings = getScoringSettings(user_id, season)
    stats = Stats()
    player_projected_stats = stats.get_all_projections(pos, season)

    projections = getPlayerProjection(scoring_settings, player_projected_stats)

    all_players = pandas.read_csv(f"all_players_{season}.csv")

    all_players.insert(0, "Projections", 0)
    for p in tqdm(projections):
        temp_index = all_players[all_players['player_id'] == p].index[0]
        all_players.loc[temp_index-1, "Projections"] = float(projections[p])

    all_players.to_csv(f"all_players_{season}_w_projections.csv")

    get_drafts = "https://api.sleeper.app/v1/league/<league_id>/drafts"

    # bid_params = {"operationName":"draft_make_offer","variables":{},"query":"mutation draft_make_offer {\n        draft_make_offer(sport: \"nfl\",player_id: \"4034\",draft_id: \"1134723274715459584\",pick_no: 3,amount: 29,slot: 7){\n          draft_id\n          pick_no\n          player_id\n          user_id\n          amount\n          metadata\n          time\n          slot\n        }\n      }"}
    # bid = requests.post("https://sleeper.com/graphql", params=bid_params)