import pandas
import requests
import csv
import xlsxwriter
import statistics
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
    pandas.options.mode.chained_assignment = None
    username = "ahstewart"
    pos = "regular"
    season = 2024

    user_id = getUserId(username)
    user = User(user_id)
    user_draft_details = user.get_all_drafts("nfl", season)
    d24 = user.get_all_drafts("nfl", season)[0]['settings']
    draft_id = user_draft_details[0]['draft_id']
    league_id = user_draft_details[0]['league_id']
    league = League(league_id)
    team_managers = league.get_users()
    manager_ids = []
    manager_names = []
    for t in team_managers:
        manager_ids.append(t['user_id'])
        manager_names.append(t['display_name'])
    managers = {ids: names for ids, names in zip(manager_ids, manager_names)}
    draft_2022 = user.get_all_drafts("nfl", 2022)
    draft_2022_picks = requests.get(f"https://api.sleeper.app/v1/draft/{draft_2022[0]['draft_id']}/picks").json()
    picks_2022 = []
    costs_2022 = []
    for d22 in draft_2022_picks:
        picks_2022.append(d22['player_id'])
        try:
            costs_2022.append((d22['metadata']['amount'], managers[d22['picked_by']]))
        except KeyError:
            costs_2022.append((d22['metadata']['amount'], d22['picked_by']))
    draft_2022_picks = {pick: cost for pick, cost in zip(picks_2022, costs_2022)}
    draft_2023 = user.get_all_drafts("nfl", 2023)
    draft_2023_picks = requests.get(f"https://api.sleeper.app/v1/draft/{draft_2023[0]['draft_id']}/picks").json()
    picks_2023 = []
    costs_2023 = []
    for d23 in draft_2023_picks:
        picks_2023.append(d23['player_id'])
        try:
            costs_2023.append((d23['metadata']['amount'], managers[d23['picked_by']]))
        except KeyError:
            costs_2023.append((d23['metadata']['amount'], d23['picked_by']))
    draft_2023_picks = {pick: cost for pick, cost in zip(picks_2023, costs_2023)}
    scoring_settings = getScoringSettings(user_id, season)
    stats = Stats()
    player_projected_stats = stats.get_all_projections(pos, season)
    player_projected_stats_2023 = stats.get_all_projections(pos, 2023)
    player_projected_stats_2022 = stats.get_all_projections(pos, 2022)
    player_stats_2023 = stats.get_all_stats(pos, 2023)
    player_stats_2022 = stats.get_all_stats(pos, 2022)


    projections = getPlayerProjection(scoring_settings, player_projected_stats)
    projections_2023 = getPlayerProjection(scoring_settings, player_projected_stats_2023)
    projections_2022 = getPlayerProjection(scoring_settings, player_projected_stats_2022)
    stats_2023 = getPlayerProjection(scoring_settings, player_stats_2023)
    stats_2022 = getPlayerProjection(scoring_settings, player_stats_2022)


    all_players = pandas.read_csv(f"all_players_{season}.csv")

    all_players.insert(0, "Projections_2024", 0)
    all_players.insert(3, "Projections_2023", 0)
    all_players.insert(1, "Projections_2022", 0)
    all_players.insert(2, "Stats_2022", 0)
    all_players.insert(4, "Stats_2023", 0)
    all_players.insert(5, "Cost_2023", 0)
    all_players.insert(6, "Cost_2022", 0)
    all_players.insert(7, "Bought_By_2023", "")
    all_players.insert(8, "Bought_By_2022", "")
    all_players.insert(9, "VORP_2024_med", 0)
    all_players.insert(10, "VORP_2024_mean", 0)
    all_players.insert(11, "VALUE", 0)

    for p in tqdm(projections):
        temp_index = all_players[all_players['player_id'] == p].index[0]
        try:
            all_players.loc[temp_index, "Projections_2024"] = float(projections[p])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Projections_2023"] = float(projections_2023[p])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Projections_2022"] = float(projections_2022[p])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Stats_2023"] = float(stats_2023[p])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Stats_2022"] = float(stats_2022[p])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Cost_2022"] = float(draft_2022_picks[p][0])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Cost_2023"] = float(draft_2023_picks[p][0])
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Bought_By_2023"] = draft_2023_picks[p][1]
        except KeyError:
            pass
        try:
            all_players.loc[temp_index, "Bought_By_2022"] = draft_2022_picks[p][1]
        except KeyError:
            pass

    positions = ["QB", "RB", "WR", "TE", "DEF", "OL", "DB", "LB", "DT", "DE", "DL", "IDL", "S", "OLB", "CB", "K"]

    all_players = all_players.loc[all_players['active'] == True]
    all_players = all_players.loc[all_players['Projections_2024'] != 0]

    writer = pandas.ExcelWriter('all_projections_2024.xlsx', engine='xlsxwriter')

    qbs = all_players[all_players['fantasy_positions'].str.contains("QB", na=False)]
    qb_raw_projections = qbs['Projections_2024'].tolist()
    qb_med = statistics.median(qb_raw_projections)
    qb_mean = statistics.mean(qb_raw_projections)
    qbs['VORP_2024_med'] = qbs['Projections_2024'] - qb_med
    qbs['VORP_2024_mean'] = qbs['Projections_2024'] - qb_mean

    rbs = all_players[all_players['fantasy_positions'].str.contains("RB", na=False)]
    rb_raw_projections = qbs['Projections_2024'].tolist()
    rb_med = statistics.median(rb_raw_projections)
    rb_mean = statistics.mean(rb_raw_projections)
    rbs['VORP_2024_med'] = rbs['Projections_2024'] - rb_med
    rbs['VORP_2024_mean'] = rbs['Projections_2024'] - rb_mean
    wrs = all_players[all_players['fantasy_positions'].str.contains("WR", na=False)]
    wr_raw_projections = wrs['Projections_2024'].tolist()
    wr_med = statistics.median(wr_raw_projections)
    wr_mean = statistics.mean(wr_raw_projections)
    wrs['VORP_2024_med'] = wrs['Projections_2024'] - wr_med
    wrs['VORP_2024_mean'] = wrs['Projections_2024'] - wr_mean
    tes = all_players[all_players['fantasy_positions'].str.contains("TE", na=False)]
    te_raw_projections = tes['Projections_2024'].tolist()
    te_med = statistics.median(te_raw_projections)
    te_mean = statistics.mean(te_raw_projections)
    tes['VORP_2024_med'] = tes['Projections_2024'] - te_med
    tes['VORP_2024_mean'] = tes['Projections_2024'] - te_mean
    defs = all_players[all_players['fantasy_positions'].str.contains("DEF", na=False)]
    def_raw_projections = defs['Projections_2024'].tolist()
    def_med = statistics.median(def_raw_projections)
    def_mean = statistics.mean(def_raw_projections)
    defs['VORP_2024_med'] = defs['Projections_2024'] - def_med
    defs['VORP_2024_mean'] = defs['Projections_2024'] - def_mean
    ks = all_players[all_players['fantasy_positions'].str.contains("K", na=False)]
    ks_raw_projections = ks['Projections_2024'].tolist()
    ks_med = statistics.median(ks_raw_projections)
    ks_mean = statistics.mean(ks_raw_projections)
    ks['VORP_2024_med'] = ks['Projections_2024'] - ks_med
    ks['VORP_2024_mean'] = ks['Projections_2024'] - ks_mean

    idls = all_players[all_players['fantasy_positions'].str.contains("OL|DB|LB|DT|DE|DL|IDL|S|OLB|CB", na=False)]
    idls_raw_projections = idls['Projections_2024'].tolist()
    idl_med = statistics.median(idls_raw_projections)
    idl_mean = statistics.mean(idls_raw_projections)
    idls['VORP_2024_med'] = idls['Projections_2024'] - idl_med
    idls['VORP_2024_mean'] = idls['Projections_2024'] - idl_mean

    flex_med = statistics.mean([rb_med, wr_med, te_med])

    total_team_med = (qb_mean * d24['slots_qb']) + (rb_mean * d24['slots_rb']) + (wr_mean * d24['slots_wr']) + (
                te_mean * d24['slots_te']) + (idl_mean * d24['slots_idp_flex']) + (ks_mean * d24['slots_k']) + (def_mean) + (flex_med * d24['slots_flex'])

    qbs['VALUE'] = qbs['Projections_2024'] / total_team_med
    rbs['VALUE'] = rbs['Projections_2024'] / total_team_med
    wrs['VALUE'] = wrs['Projections_2024'] / total_team_med
    tes['VALUE'] = tes['Projections_2024'] / total_team_med
    ks['VALUE'] = ks['Projections_2024'] / total_team_med
    defs['VALUE'] = defs['Projections_2024'] / total_team_med
    idls['VALUE'] = idls['Projections_2024'] / total_team_med

    qbs.to_excel(writer, sheet_name="QB")
    rbs.to_excel(writer, sheet_name="RB")
    wrs.to_excel(writer, sheet_name="WR")
    defs.to_excel(writer, sheet_name="DEF")
    tes.to_excel(writer, sheet_name="TE")
    ks.to_excel(writer, sheet_name="K")
    idls.to_excel(writer, sheet_name="IDL")

    writer.save()

    all_players.to_csv(f"all_players_{season}_w_projections.csv")

    get_drafts = "https://api.sleeper.app/v1/league/<league_id>/drafts"

    # bid_params = {"operationName":"draft_make_offer","variables":{},"query":"mutation draft_make_offer {\n        draft_make_offer(sport: \"nfl\",player_id: \"4034\",draft_id: \"1134723274715459584\",pick_no: 3,amount: 29,slot: 7){\n          draft_id\n          pick_no\n          player_id\n          user_id\n          amount\n          metadata\n          time\n          slot\n        }\n      }"}
    # bid = requests.post("https://sleeper.com/graphql", params=bid_params)