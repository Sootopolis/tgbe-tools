import requests
from datetime import datetime
from components import *
# import csv
# import json
# from json import JSONDecodeError


# create request header and start session
setup = get_setup()
headers = generate_headers(setup.username, setup.email)
session = requests.session()
session.headers.update(headers)

# get current members from api
url = "https://api.chess.com/pub/club/{}/members".format(setup.club)
response = session.get(url)
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    raise SystemExit("connection error - error code {}".format(response.status_code))
content = response.json()
curr_members = dict()
for category in ("weekly", "monthly", "all_time"):
    for entry in content[category]:
        curr_members[entry["username"]] = entry["joined"]

# get members in local record
prev_members = dict()
with open("members.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    for username, player_id, timestamp in reader:
        prev_members[username] = [int(player_id), int(timestamp)]

# get former members in local record
lost_members = dict()
with open("lost_members.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    for username, player_id, timestamp in reader:
        lost_members[username] = [int(player_id), int(timestamp)]

# get username changes in local record
username_changes = dict()
with open("username_changes.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    for new_name, old_name, player_id in reader:
        username_changes[new_name] = [old_name, int(player_id)]



# close session
session.close()
