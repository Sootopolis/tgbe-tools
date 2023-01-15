import csv
import requests
from pathlib import Path
from components import Setup, Member, Candidate, get_player_homepage, print_bold
from datetime import datetime, timezone

records = Path().resolve() / "records"

# get members in local record
record_members = set()
former_members = dict()
with open(records / "members.csv") as stream:
    reader = csv.reader(stream)
    header_members = next(reader)
    for row in reader:
        player = Member(*row)
        if player.is_former or player.is_closed:
            former_members[player.player_id] = player
        else:
            record_members.add(player)

# get setup, create request header, start session
setup = Setup()
setup.load()
session = requests.session()
session.headers.update(setup.headers())

# get the latest members from api
latest_members = set()
url = setup.club.get_members()
response = session.get(url, timeout=10)
if response.status_code != 200:
    raise SystemExit("cannot get member list - {}".format(response.status_code))
content = response.json()
for category in ("weekly", "monthly", "all_time"):
    for entry in content[category]:
        username = entry["username"]
        timestamp = entry["joined"]
        latest_members.add(
            Member(
                username=username, timestamp=timestamp, is_closed=False, is_former=False
            )
        )

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
        raise SystemExit(
            "cannot get player_id for {} - error code {}".format(
                player.username, response.status_code
            )
        )
    else:
        content = response.json()
        player.player_id = content["player_id"]

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
            left.pop(player_id)
        elif response.json()["status"][:6] == "closed":
            closed.append(L.username)
            L.is_closed = True
            left.pop(player_id)
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
    print("goners:")
    for player in left.values():
        print(player.username, player.get_homepage())
if rejoined:
    print("players who have left and returned:")
    for username in rejoined:
        print(username, get_player_homepage(username))
if closed:
    print("account closures:")
    for username in closed:
        print(username, get_player_homepage(username))
if reopened:
    print("accounts closed and reopened:")
    for username in closed:
        print(username, get_player_homepage(username))
if renamed:
    print("username changes:")
    for old_name, new_name in renamed:
        print(old_name, "->", new_name, get_player_homepage(new_name))
if renamed_left:
    print(
        "players who have changed their usernames and either left or closed their accounts:"
    )
    for username in renamed_left:
        print(username, get_player_homepage(username))
if renamed_rejoined:
    print("players who have changed their usernames, left, and rejoined:")
    for old_name, new_name in renamed_rejoined:
        print(old_name, "->", new_name, get_player_homepage(new_name))
if renamed_reopened:
    print(
        "players whose accounts were closed and are reopened and who have changed their usernames:"
    )
    for old_name, new_name in renamed_reopened:
        print(old_name, "->", new_name, get_player_homepage(new_name))
if came:
    print("newbies:")
    for player in came.values():
        print(player.username, player.get_homepage())
        record_members.add(player)

if (
    __name__ == "__main__"
    or left
    or rejoined
    or closed
    or reopened
    or renamed
    or renamed_left
    or renamed_rejoined
    or renamed_reopened
    or came
):
    print_bold("total number: {}".format(len(latest_members)))
    print(datetime.now(tz=timezone.utc))

members = []
for member in record_members:
    members.append(member)
for member in former_members.values():
    members.append(member)
members.sort()

with open(records / "members.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerow(header_members)
    for member in members:
        writer.writerow(member.to_members_row())

if came:

    candidates = []
    with open(records / "scanned.csv") as stream:
        reader = csv.reader(stream)
        header_scanned = next(reader)
        for row in reader:
            candidate = Candidate(*row)
            if candidate.player_id in came:
                candidate.joined = True
                candidate.expiry = 9999999999
            candidates.append(candidate)

    with open(records / "scanned.csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(header_scanned)
        for candidate in candidates:
            writer.writerow(candidate.to_csv_row())
