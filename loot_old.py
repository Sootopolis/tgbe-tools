import json
from time import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
from requests.structures import CaseInsensitiveDict
from components_old import *
from tqdm import tqdm

target = int(input("number of players to invite: "))
club_name = input("enter club name (as in url; leave empty to quit): ").strip(" /")
if not club_name:
    raise SystemExit

# constraints
enter_cache = True
clear_cache = True
min_cm_played = 12  # int(input("minimum number of team match games in last 90 days: "))
min_cm_ongoing = 2  # int(input("minimum number of ongoing games: "))
max_ongoing = 100  # int(input("maximum number of ongoing games: "))
max_clubs = 32  # int(input("maximum number of clubs: "))
min_rating = 1000  # int(input("minimum rating (inclusive): "))
max_rating = 2300  # int(input("maximum rating (inclusive): "))
# min_win_rate = 0.4  # int(input("minimum win rate: "))
# max_win_rate = 0.8  # int(input("maximum win rate: "))
min_score_rate = 0.45
max_score_rate = 0.85
max_time_per_move = timedelta(hours=18)
max_offline = timedelta(hours=48)
avoid_admins = True

# find yyyy/mm
start = int(time())
current_datetime = datetime.fromtimestamp(start)
archive_datetime = current_datetime - timedelta(days=90)
months = []
while archive_datetime <= current_datetime:
    months.append("{}/{:>02}".format(archive_datetime.year, archive_datetime.month))
    archive_datetime += relativedelta(months=+1)
months.reverse()
archive_datetime = current_datetime - timedelta(days=90)

# clear cache and get scanned players
try:
    with open("scanned_players.json", "r") as scanned_json:
        scanned = json.load(scanned_json)
    if clear_cache:
        for key in list(scanned.keys()):
            if scanned[key] <= start:
                del scanned[key]
except json.JSONDecodeError:
    scanned = {}

# start session
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["From"] = "python 3.10, python-requests/2.28.1; username: wallace_wang; contact: yuzhuo.w@gmail.com"
session = requests.session()
session.headers.update(headers)

# check if victim club exists and get the victim club"s admins
response = session.get(f"https://api.chess.com/pub/club/{club_name}", timeout=5)
if response.status_code != 200:
    print("connection error")
    raise SystemExit
content = response.json()
if content.get("code", 1) == 0:
    print("club does not exist")
    raise SystemExit
club_admins = set(content["admin"])

# get players to examine
response = session.get(f"https://api.chess.com/pub/club/{club_name}/members", timeout=5)
if response.status_code != 200:
    print("connection error")
    raise SystemExit
content = response.json()
candidates = []
with open("members.json") as membership_json:
    membership = json.load(membership_json)
with open("lost_members.json") as lost_members_json:
    lost_members = json.load(lost_members_json)
with open("invited.txt") as invited_txt:
    invited = set(invited_txt.read().strip(" \n").split("\n"))
for category in ("weekly", "monthly", "all_time"):
    for member in content[category]:
        # skip existing members
        if member["username"].lower() in membership:
            continue
        # skip former members
        if member["username"].lower() in lost_members:
            continue
        # skip already invited players
        if member["username"].lower() in invited:
            continue
        # skip cached uninvitable players
        if member["username"].lower() in scanned:
            continue
        # skip admins
        if avoid_admins:
            if f"https://api.chess.com/pub/player/{member['username'].lower()}" in club_admins:
                continue
        candidates.append(member["username"].lower())

# quit if candidates is empty
if not candidates:
    print("no players to scan")
    raise SystemExit

# make progress bars
candidates_bar = tqdm(total=len(candidates), desc="candidates", position=0, colour="blue", unit="players")
invitables_bar = tqdm(total=target, desc="invitables", position=1, colour="yellow", unit="players")

# examine players
invitable = []
try:
    for player in candidates:
        candidates_bar.update()

        # get player profile
        try:
            response = session.get(f"https://api.chess.com/pub/player/{player}", timeout=5)
        except requests.exceptions.RequestException:
            continue
        if response.status_code != 200:
            continue
        content = response.json()

        # eliminates players offline for too long
        if current_datetime - datetime.fromtimestamp(content["last_online"]) > max_offline:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # get player clubs
        try:
            response = session.get(f"https://api.chess.com/pub/player/{player}/clubs", timeout=5)
        except requests.exceptions.RequestException:
            continue
        if response.status_code != 200:
            continue
        content = response.json()

        # eliminates players with too many clubs
        if len(content["clubs"]) > max_clubs:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # get player stats
        try:
            response = session.get(f"https://api.chess.com/pub/player/{player}/stats", timeout=5)
        except requests.exceptions.RequestException:
            continue
        if response.status_code != 200:
            continue
        content = response.json()

        # eliminates players who don"t play daily
        if "chess_daily" not in content:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # eliminates players who move too slow
        if timedelta(seconds=content["chess_daily"]["record"]["time_per_move"]) > max_time_per_move:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # eliminates players not in rating range
        if (
            content["chess_daily"]["last"]["rating"] < min_rating or
            content["chess_daily"]["last"]["rating"] > max_rating
        ):
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # eliminates players who lose or win too much
        wins = content["chess_daily"]["record"]["win"]
        losses = content["chess_daily"]["record"]["loss"]
        draws = content["chess_daily"]["record"]["draw"]
        if "chess960_daily" in content:
            wins += content["chess960_daily"]["record"]["win"]
            losses += content["chess960_daily"]["record"]["loss"]
            draws += content["chess960_daily"]["record"]["draw"]
        score_rate = (wins + draws / 2) / (wins + losses + draws)
        if score_rate < min_score_rate or score_rate > max_score_rate:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # streamlines later procedures for players without any timeout
        no_timeout = content["chess_daily"]["record"]["timeout_percent"] == 0

        # get player ongoing games
        try:
            response = session.get(f"https://api.chess.com/pub/player/{player}/games", timeout=5)
        except requests.exceptions.RequestException:
            continue
        if response.status_code != 200:
            continue
        content = response.json()

        # eliminates players with too many games ongoing
        if len(content["games"]) > max_ongoing:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # eliminates players with too few team match games ongoing
        cm_played = 0
        for game in content["games"]:
            if "match" in game:
                cm_played += 1
        if cm_played < min_cm_ongoing:
            if enter_cache:
                scanned[player] = int(start + timedelta(days=30).total_seconds())
            continue

        # invites players without timeouts and with enough team match games ongoing
        if no_timeout and cm_played >= min_cm_played:
            invitable.append(player)
            invitables_bar.update()
            if len(invitable) >= target:
                break
            continue

        # get player monthly game archive
        is_invitable = True
        for month in months:
            try:
                response = session.get(f"https://api.chess.com/pub/player/{player}/games/{month}", timeout=5)
            except requests.exceptions.RequestException:
                is_invitable = False
                break
            if response.status_code != 200:
                is_invitable = False
                break
            content = response.json()
            content["games"].reverse()

            # check each game
            for game in content["games"]:
                if "match" in game:
                    if datetime.fromtimestamp(game["end_time"]) <= archive_datetime:
                        continue
                    cm_played += 1

                    # invite players without timeout and with enough team match games played
                    if no_timeout:
                        if cm_played >= min_cm_played:
                            break

                    # eliminate players with team match timeouts
                    else:
                        if game["white"]["username"].lower() == player:
                            if game["white"]["result"] == "timeout":
                                is_invitable = False
                                if enter_cache:
                                    scanned[player] = game["end_time"] + int(timedelta(days=90).total_seconds())
                                break
                        else:
                            if game["black"]["result"] == "timeout":
                                is_invitable = False
                                if enter_cache:
                                    scanned[player] = game["end_time"] + int(timedelta(days=90).total_seconds())
                                break

            # check if further scan is needed
            if not is_invitable:
                break
            if no_timeout and cm_played >= min_cm_played:
                break

        # invite players without timeout who played enough games
        if is_invitable:
            if cm_played >= min_cm_played:
                invitable.append(player)
                invitables_bar.update()
                if len(invitable) >= target:
                    break

            # eliminate players without enough team match games
            else:
                if enter_cache:
                    scanned[player] = int(start + timedelta(days=30).total_seconds())

    # close bars when either the target or the full length of candidates is reached
    candidates_bar.close()
    invitables_bar.close()

# close bars if
except KeyboardInterrupt:
    candidates_bar.close()
    invitables_bar.close()
    # this is to avoid a bug where KeyboardInterrupt causes the first bar to duplicate
    # https://github.com/tqdm/tqdm/issues/1345
    invitables_bar.display("", -3)

session.close()

# update cache
if enter_cache:
    # scanned = dict(sorted(scanned.items()))
    with open("scanned_players.json", "w") as scanned_json:
        json.dump(scanned, scanned_json, sort_keys=True, indent=2)

# output results
print(f"players invitable ({len(invitable)}):")
if invitable:
    for player in invitable:
        print_bold(player, end=" ")
    print()
else:
    print("(none)")

# output runtime
end = int(time())
print(f"runtime: {timedelta(seconds=(end - start))}")

# asks the user whether to add the invitable players to invited.txt
if invitable:
    update_invited(invitable)
