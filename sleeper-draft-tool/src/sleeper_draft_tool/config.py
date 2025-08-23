# Contents of src/sleeper_draft_tool/config.py

class Config:
    USERNAME = "ahstewart"  # Sleeper username
    API_ENDPOINT = "https://api.sleeper.app/v1/" # api is unauthenticated
    STATS_ENDPOINT = "https://api.sleeper.com/"  # endpoint for stats
    LEAGUE_ID = 1220874215918407680  # id of league in question
    SPORT = "nfl"  # sport type
    SEASON = 2025  # current season
    SEASON_TYPE = "regular"  # regular or playoff
    DRAFT_AMOUNT = 200 # number of dollars each team has to draft with
