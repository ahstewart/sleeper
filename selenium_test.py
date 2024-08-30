from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import json
import csv
from sleeper_wrapper import Stats, Players, User, League
from operator import itemgetter
from tqdm import tqdm
import numpy as np

def getUserId(username):
    user_data = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
    return user_data["user_id"]

def getScoringSettings(userId, year):
    league = requests.get(f"https://api.sleeper.app/v1/user/{userId}/leagues/nfl/{year}").json()[0]
    return league["scoring_settings"]

# scrape draft board HTML and return a dictionary of each team's picks and amount paid
def getPicksfromDraftHTML(draft_soup, num_weeks, player_list, scoring_settings, year):
    teams = draft_soup.find_all("div", "team-column")
    draft_results = {}
    for t in tqdm(teams):
        team_name = t.contents[0].h1.contents[0]
        draft_results[team_name] = {}
        picks = t.find_all("div", "cell-container")
        for p in picks:
            try:
                cost = int(p.find("div","pick").contents[0][1:])
                player_id = p.img['aria-label'].split()[-1]
                player_name = getPlayerName(player_list, player_id)
                draft_results[team_name][player_name] = {}
                draft_results[team_name][player_name]['cost'] = cost
                # calculate player's total point in num_weeks and add to the dictionary
                score = 0
                for w in range(num_weeks):
                    score += calcScore(w+1, scoring_settings, player_id, year)
                draft_results[team_name][player_name]['total_points'] = score
            except (TypeError, ValueError) as e:
                try:
                    print("\nPlayer not found, might be a defense. Trying different method...")
                    cost = int(p.find("div", "pick").contents[0][1:])
                    player_id = p.find("div", "avatar-player")['aria-label'].split()[-1]
                    player_name = getPlayerName(player_list, player_id)
                    draft_results[team_name][player_name] = {}
                    draft_results[team_name][player_name]['cost'] = cost
                    # calculate player's total point in num_weeks and add to the dictionary
                    score = 0
                    for w in range(num_weeks):
                        score += calcScore(w+1, scoring_settings, player_id, year)
                    draft_results[team_name][player_name]['total_points'] = score
                    print("Success!")
                except (TypeError, ValueError) as e:
                    print("Fail :( This pick may not have been made")
    return draft_results

def getDraftId(userId, year):
    user = User(userId)
    user_draft_details = user.get_all_drafts("nfl", season)
    return user_draft_details[0]['draft_id']

def getLeagueId(userId, year):
    user = User(userId)
    user_draft_details = user.get_all_drafts("nfl", season)
    return user_draft_details[0]['league_id']

# returns a team name string given a user ID
def getTeamName(user_dict, userId):
    team_name = None
    for u in user_dict:
        if u['user_id'] == userId:
            team_name = u['display_name']
    return team_name

# return a player name string given a player ID
def getPlayerName(player_list, player_id):
    try:
        return player_list[player_id]['full_name']
    except KeyError:
        return player_list[player_id]['first_name'] + " " + player_list[player_id]['last_name']

# calculate a player's score for a given week based on a set of scoring settings
def calcScore(week, scoring_settings, player_id, year="2023"):
    stats = Stats()
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

def getDraftResults(draft_dict, player_list, week_num, scoring_settings):
    thang = {}
    for team_name in tqdm(draft_dict):
        thang[team_name] = {}
        for w in range(week_num):
            thang[team_name][f"week {w}"] = {}
            for players in draft_dict[team_name]:
                player_name = getPlayerName(player_list, players)
                thang[team_name][f"week {w}"][player_name] = calcScore(w+1, scoring_settings, players, year=season)
    return thang

# calculate the total points scored for each team
def calcPointTotals(draft_scores):
    totals = []
    score = 0
    for guys in draft_scores:
        for weeks in draft_scores[guys]:
            for dudes in draft_scores[guys][weeks]:
                score += draft_scores[guys][weeks][dudes]
        totals.append((guys, score))
        score = 0
    return totals

def doDraftAnalysis(userName, year, week_num, selenium_driver_path):
    print(f"\nAnalyzing the {year} draft")
    driver = webdriver.Firefox(executable_path=selenium_driver_path)
    userId = getUserId(userName)
    draftId = getDraftId(userId, year)
    driver.get(f"https://sleeper.com/draft/nfl/{draftId}")
    theSoup = BeautifulSoup(driver.page_source, 'html.parser')
    players_obj = Players()
    all_players = players_obj.get_all_players()
    scoring = getScoringSettings(userId, year)
    draftDict = getPicksfromDraftHTML(theSoup, week_num, all_players, scoring, year)
    # draftResults = getDraftResults(draftDict, all_players, week_num, scoring)
    # draftScoreTotals = calcPointTotals(draftResults)
    return draftDict

def writeTotals(draftTotals, filename):
    with open(filename, mode='w', newline='') as csvfile:
        csvfile = csv.writer(csvfile)
        for i in draftTotals:
            csvfile.writerow(i)

if __name__ == "__main__":
    # configs
    username = "ahstewart"
    season = "2023"
    week_num = 15
    csv_filename = "total_draft_points_2023"
    driver_path = "C:\\Users\\ahste\\Downloads\\geckodriver-v0.33.0-win64\\geckodriver.exe"
    draft_costs = doDraftAnalysis(username, season, week_num, driver_path)
    # writeTotals(draft_results, csv_filename)