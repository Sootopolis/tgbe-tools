import requests
import json
from json.decoder import JSONDecodeError
from datetime import datetime
from components import *
# types of membership changes to be dealt with:
# 1. someone left (username doesn't appear in new record, player id not equal to anyone only in new record)
# 2. someone came (username doesn't appear in old record, player id not equal to anyone only in old record)
# 3. someone left and returned (only timestamp changes)
# 4. someone changed name (username doesn't appear in old record, player id equal to someone only in old record)
#    TODO: the program is currently not tackling this very well
# 5. someone left, returned, and changed name at some point (username doesn't appear in old record, timestamp changes,
#    player id equal to someone only in old record)
#    TODO: the program is currently not tackling this at all

url = "https://api.chess.com/pub/club/the-great-british-empire/members"
response = requests.get(url)
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    raise SystemExit
content = response.json()

new_members = {}
for category in ("weekly", "monthly", "all_time"):
    for entry in content[category]:
        new_members[entry["username"]] = entry["joined"]
with open("members.json", "r") as members_json:
    try:
        old_members = json.load(members_json)
    except JSONDecodeError:
        old_members = {}
with open("lost_members.json", "r") as lost_members_json:
    try:
        lost_members = json.load(lost_members_json)
    except JSONDecodeError:
        lost_members = {}
came = list(new_members.items() - old_members.items())
went = list(old_members.items() - new_members.items())
came.sort(key=lambda x: x[1])
went.sort(key=lambda x: x[1])
# now came and went are lists of pairs of username and timestamp

changed = []
while came and went:
    if came[0][1] <= went[-1][1]:
        for i in range(len(went)):
            if went[i][1] == came[0][1]:
                changed.append((went[i][0], came[0][0]))
                del came[0]
                del went[i]
                break
    else:
        break

if came:
    print("arrivals:")
    for i in range(len(came)):
        print(came[i][0], datetime.fromtimestamp(came[i][1]))
        if came[i][0] in lost_members:
            del lost_members[came[i][0]]

if went:
    print("departures:")
    for i in range(len(went)):
        print(went[i][0], datetime.fromtimestamp(went[i][1]))
        lost_members[went[i][0]] = went[i][1]
    with open("lost_members.json", "w") as lost_members_json:
        # lost_members = dict(sorted(lost_members.items()))
        json.dump(lost_members, lost_members_json, sort_keys=True, indent=2)

if changed:
    print_bold("NAME CHANGES:")
    for i in range(len(changed)):
        print(f"{changed[i][0]} is now known as {changed[i][1]}")

# new_members = dict(sorted(new_members.items()))
with open("members.json", "w") as members_json:
    json.dump(new_members, members_json, sort_keys=True, indent=2)
print(f"total members: {len(new_members)}")
