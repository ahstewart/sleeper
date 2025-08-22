import requests
import json
import csv
from sleeper_wrapper import Stats
from sleeper_wrapper import Players

username = "ahstewart"
user_data = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
user_id = user_data["user_id"]
user_endpoint = f"https://api.sleeper.app/v1/user/{user_id}"
season = "2022"
position = "RB"
type = "stats"
path = f"C:\\Users\\ahste\\OneDrive\\sleeps\\{season}"

league = requests.get(f"{user_endpoint}/leagues/nfl/{season}").json()[0]
scoring = league["scoring_settings"]
print("There are " + str(len(scoring)) + " scoring settings")

# get projections for a season and a position
if position == 'IDP':
    proj = requests.get(f"https://api.sleeper.com/{type}/nfl/{season}?season_type=regular&position[]=DB&position[]=DL&position[]=LB&order_by=pts_std").json()
else:
    proj = requests.get(f"https://api.sleeper.com/{type}/nfl/{season}?season_type=regular&position[]={position}&order_by=pts_std").json()


# clean up all lame players and lame data
proj = [i for i in proj if "pts_std" in i['stats']]
proj_stats = [i['stats'] for i in proj]
max_fields = len(proj_stats[0])
max_fields_index = 0
for i in range(len(proj_stats)):
    proj_stats[i].update({"player_id":proj[i]['player_id']})
    proj_stats[i].update({"first_name": proj[i]['player']['first_name']})
    proj_stats[i].update({"last_name": proj[i]['player']['last_name']})
    proj_stats[i].update({"injury_status": proj[i]['player']['injury_status']})
    if len(proj_stats[i]) > max_fields:
        max_fields_index = i
        max_fields = len(proj_stats[i])

# get headers
raw_headers = list(proj_stats[max_fields_index].keys())
headers = ["first_name", "last_name", "player_id", "injury_status"]
for i in raw_headers:
    headers.append(i)
headers = headers[:-4]
if position == 'RB':
    headers.append('def_kr_td')
    headers.append('idp_tkl_ast')
    headers.append('idp_tkl')
    headers.append('rush_td_50p')
    headers.append('idp_tkl_solo')
    headers.append('fum_lost')
    headers.append('penalty')
    headers.append('rush_btkl')
    headers.append('penalty_yd')
    headers.append('rush_40p')
    headers.append('bonus_rush_yd_100')
    headers.append('pass_int_td')
    headers.append('bonus_rush_rec_yd_100')
    headers.append('rush_td_40p')
    headers.append('rush_td_50p')
    headers.append('rec_rz_tgt')
    headers.append('st_snp')
    headers.append('rec_0_4')
    headers.append('pts_idp')
    headers.append('idp_ff')
    headers.append('rec_td_lng')
    headers.append('rec_td')
    headers.append('rush_2pt')
    headers.append('rec_2pt')
    headers.append('rec_td_50p')
    headers.append('rec_td_40p')
    headers.append('bonus_rec_yd_100')
    headers.append('st_tkl_solo')
    headers.append('pass_sack')
    headers.append('pass_sack_yds')
    headers.append('pass_inc')
    headers.append('pass_int')
    headers.append('kr_ypa')
    headers.append('kr_lng')
    headers.append('kr_yd')
    headers.append('kr')
    headers.append('st_td')
    headers.append('st_ff')
    headers.append('pr_lng')
    headers.append('pr')
    headers.append('pr_yd')
    headers.append('pr_ypa')
    headers.append('fum_rec_td')
    headers.append('st_fum_rec')
    headers.append('def_snp')
elif position == 'QB':
    headers.append('fum_lost')
    headers.append('penalty')
    headers.append('rush_btkl')
    headers.append('penalty_yd')
    headers.append('rush_40p')
    headers.append('bonus_rush_yd_100')
    headers.append('pass_int_td')
    headers.append('bonus_rush_rec_yd_100')
    headers.append('rush_td_40p')
    headers.append('rush_td_50p')
    headers.append('rec_rz_tgt')
    headers.append('st_snp')
    headers.append('rec_0_4')
    headers.append('pts_idp')
    headers.append('idp_ff')
    headers.append('rec_td_lng')
    headers.append('rec_td')
elif position == 'WR':
    headers.append('def_kr_td')
    headers.append('rec_2pt')
elif position == 'DEF':
    headers.append('def_kr_td')
    headers.append('pr_td')
elif position == 'TE':
    headers.append('bonus_rec_te')
elif position == 'IDP':
    headers.append('idp_tkl')
    headers.append('idp_tkl_ast')
    headers.append('idp_int')
    headers.append('idp_sack')
    headers.append('idp_tkl_solo')
    headers.append('idp_fum_rec')
    headers.append('idp_ff')
    headers.append('pass_int_td')

# write to csv
#with open(f'{path}\\{position}_{season}_{type}.csv', 'w') as csvfile:
 #   writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
  #  writer.writeheader()
   # writer.writerows(proj_stats)