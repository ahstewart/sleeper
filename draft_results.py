import requests
import json
import csv
from sleeper_wrapper import Stats, Players, User, League
from operator import itemgetter
from tqdm import tqdm
import numpy as np

username = "ahstewart"
season = "2022"
week_num = 14
csv_filename = "total_draft_points_2022.csv"

def getScoringSettings(userId, year):
    league = requests.get(f"https://api.sleeper.app/v1/user/{userId}/leagues/nfl/{year}").json()[0]
    return league["scoring_settings"]

def getUserId(username):
    user_data = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
    return user_data["user_id"]

user_id = getUserId(username)
user = User(user_id)
user_draft_details = user.get_all_drafts("nfl", season)
draft_id = user_draft_details[0]['draft_id']
league_id = user_draft_details[0]['league_id']
league_obj = League(league_id)
league_users = league_obj.get_users()

def getTeamName(user_dict, userId):
    team_name = None
    for u in user_dict:
        if u['user_id'] == userId:
            team_name = u['display_name']
    return team_name

players = Players()
all_players = players.get_all_players()

def getPlayerName(player_list, player_id):
    try:
        return player_list[player_id]['full_name']
    except KeyError:
        return player_list[player_id]['first_name'] + " " + player_list[player_id]['last_name']

stats = Stats()

def calcScore(week, scoring_settings, player_id, year="2023"):
    score = 0
    try:
        weekStats = stats.get_week_stats("regular", year, week)
        playerStats = stats.get_player_week_stats(weekStats, player_id)
        for p in playerStats:
            try:
                score += playerStats[p]*scoring_settings[p]
            except KeyError:
                pass
    except TypeError:
        pass
    return score

# calculate weekly scores per drafted player and append to each list
def getDraftPerformance(league_id, draft_id, week_num, scoring, player_list, season):
    league_obj = League(league_id)
    league_users = league_obj.get_users()
    all_draft_picks = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()
    all_picks_min = [[i['player_id'], i['picked_by']] for i in all_draft_picks]
    all_picks_min.sort(key=itemgetter(1))
    thang = {}
    for lusers in tqdm(league_users):
        team_name = getTeamName(league_users, lusers['user_id'])
        thang[team_name] = {}
        for w in range(week_num):
            thang[team_name][f"week {w}"] = {}
            for players in all_picks_min:
                if players[1] == lusers['user_id']:
                    player_name = getPlayerName(player_list, players[0])
                    thang[team_name][f"week {w}"][player_name] = calcScore(w+1, scoring, players[0], year=season)
    return thang

def getPicksfromDraftHTML(draft_soup):
    teams = draft_soup.find_all("div", "team_column")
    draft_results = {}
    for t in teams:
        team_name = t.contents[0].h1.contents[0]
        draft_results[team_name] = {}
        picks = t.find_all("div", "cell-container")
        for p in picks:
            cost = int(p.find("div","pick").contents[0][1:])
            player_id = p.img['aria-label'].split()[-1]
            draft_results[team_name][player_id] = cost


if __name__ == '__main__':
    # calculate the total points scored for each team
    totals = []
    score = 0
    for guys in thang:
        for weeks in thang[guys]:
            for dudes in thang[guys][weeks]:
                score += thang[guys][weeks][dudes]
        totals.append((guys, score))
        score = 0

    # write to a csv
    with open(csv_filename, mode='w', newline='') as csvfile:
        csvfile = csv.writer(csvfile)
        for i in totals:
            csvfile.writerow(i)

