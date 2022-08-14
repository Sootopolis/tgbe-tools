import requests
from components import Setup, Member, get_player_page, print_bold
import csv

# get members in local record
record_members = set()
former_members = dict()
with open("members.csv") as stream:
    reader = csv.reader(stream)
    header = next(reader)
    for username, player_id, timestamp, is_closed, is_former in reader:
        player = Member(
            username=username,
            player_id=int(player_id),
            timestamp=int(timestamp),
            is_closed=bool(int(is_closed)),
            is_former=bool(int(is_former))
        )
        if player.is_former or player.is_closed:
            former_members[player_id] = player
        else:
            record_members.add(player)

# get setup, create request header, start session
setup = Setup()
setup.load()
session = requests.session()
session.headers.update({"from": setup.email})

# get the latest members from api
latest_members = set()
url = setup.club.get_members()
response = session.get(url)
if response.status_code != 200:
    raise SystemExit("cannot get member list - {}".format(response.status_code))
content = response.json()
for category in ("weekly", "monthly", "all_time"):
    for entry in content[category]:
        username = entry["username"]
        timestamp = entry["joined"]
        latest_members.add(Member(
            username=username,
            timestamp=timestamp,
            is_closed=False,
            is_former=False
        ))

# compare members
# two members are considered equal if the username,
# player_id (if both have it), timestamp (if both have it)
# are all equal
left = record_members - latest_members
came = latest_members - record_members

# get player_ids of new members
for player in came:
    response = session.get(player.get_profile())
    if response.status_code != 200:
        print("cannot get player_id for {} - error code {}".format(player.username, response.status_code))
        player_id = 0
    else:
        content = response.json()
        player_id = content["player_id"]
    player.player_id = player_id

left = {player.player_id: player for player in left}
came = {player.player_id: player for player in came}

# possible membership changes other than came and left
closed = []
reopened = []
rejoined = []
renamed = []
renamed_left = []
renamed_rejoined = []
renamed_reopened = []


# figure out specifics of lost members
for player_id in list(left.keys()):
    L: Member = left[player_id]
    if player_id in came:
        C: Member = came[player_id]
        if L.username == C.username:
            rejoined.append(L.username)
            L.timestamp = C.timestamp
        elif L.timestamp == C.timestamp:
            renamed.append((L.username, C.username))
            L.username = C.username
        else:
            renamed_rejoined.append((L.username, C.username))
            L.username = C.username
            L.timestamp = C.timestamp
        came.pop(player_id)
        left.pop(player_id)
    else:
        response = session.get(L.get_profile())
        if response.status_code != 200:
            renamed_left.append(L.username)
            L.is_former = True
        elif response.json()["status"][:6] == "closed":
            closed.append(L.username)
            L.is_closed = True
        else:
            L.is_former = True

session.close()

# figure out specifics of new members
for player_id in list(came.keys()):
    C: Member = came[player_id]
    if player_id not in former_members:
        continue
    F: Member = former_members[player_id]
    if C.username != F.username:
        if F.is_closed:
            renamed_reopened.append((F.username, C.username))
            F.is_closed = False
        else:
            renamed_rejoined.append((F.username, C.username))
            F.is_former = False
        F.username = C.username
        F.timestamp = C.timestamp
    elif F.is_closed:
        reopened.append(F.username)
        F.timestamp = C.timestamp
        F.is_closed = False
    else:
        rejoined.append(F.username)
        F.timestamp = C.timestamp
        F.is_former = False
    came.pop(player_id)

# print results
if left:
    print("players who have left:")
    for player in left.values():
        print(player.username, player.get_homepage())
if rejoined:
    print("players who have left and returned:")
    for username in rejoined:
        print(username, get_player_page(username))
if closed:
    print("players whose accounts are closed:")
    for username in closed:
        print(username, get_player_page(username))
if reopened:
    print("players whose accounts were closed and are reopened:")
    for username in closed:
        print(username, get_player_page(username))
if renamed:
    print("players who have changed their usernames:")
    for old_name, new_name in renamed:
        print(old_name, "->", new_name, get_player_page(new_name))
if renamed_left:
    print("players who have changed their usernames")
    print("and either left or closed their accounts:")
    for old_name, new_name in renamed_left:
        print(old_name, "->", new_name, get_player_page(new_name))
if renamed_rejoined:
    print("players who have changed their usernames, left, and rejoined:")
    for old_name, new_name in renamed_rejoined:
        print(old_name, "->", new_name, get_player_page(new_name))
if renamed_reopened:
    print("players whose accounts were closed and are reopened")
    print("and who have changed their usernames:")
    for old_name, new_name in renamed_reopened:
        print(old_name, "->", new_name, get_player_page(new_name))
if came:
    print("players who have joined:")
    for player in came.values():
        print(player.username, player.get_homepage())
        record_members.add(player)

if (
    __name__ == "__main__" or
    left or
    rejoined or
    closed or
    reopened or
    renamed or
    renamed_left or
    renamed_rejoined or
    renamed_reopened or
    came
):
    print_bold("total number: {}".format(len(latest_members)))

members = []
for member in record_members:
    members.append([
        member.username,
        member.player_id,
        member.timestamp,
        int(member.is_closed),
        int(member.is_former)
    ])
for member in former_members.values():
    members.append([
        member.username,
        member.player_id,
        member.timestamp,
        int(member.is_closed),
        int(member.is_former)
    ])
members.sort()

with open("members.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerow(header)
    writer.writerows(members)
