import csv
from datetime import datetime, timedelta, timezone
import requests
from requests.exceptions import RequestException
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from components import Setup, Candidate, Club, print_bold

# load setup
setup = Setup()
setup.load()

# set target number and victim club
target = int(input("number of players to invite: "))
club = Club(input("enter club name as in url; leave empty to quit: ").strip(" /").split("/")[-1])
if not club.name:
    raise SystemExit("club name not provided")

# find yyyy/mm
now_datetime = datetime.now(timezone.utc)
now = int(now_datetime.timestamp())
ninty = now_datetime - timedelta(days=90)
months = []
while ninty <= now_datetime:
    months.append("{}/{:>02}".format(ninty.year, ninty.month))
    ninty += relativedelta(months=+1)
months.reverse()
ninty = now_datetime - timedelta(days=90)

# get members and former members in record
with open("members.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    members = set()
    for entry in reader:
        members.add(entry[0])

# # get and clear uninvitable cache
# with open("uninvitables.csv") as stream:
#     reader = csv.reader(stream)
#     header_uninvitables = next(reader)
#     uninvitables = dict()
#     if setup.clear_uninvitable_cache:
#         for username, timestamp in reader:
#             if int(timestamp) <= now:
#                 continue
#             uninvitables[username] = int(timestamp)
#     else:
#         for username, timestamp in reader:
#             uninvitables[username] = int(timestamp)

# # get invited players in record
# with open("invited.csv") as stream:
#     reader = csv.reader(stream)
#     header_invited = next(reader)
#     invited = dict()
#     for username, timestamp in reader:
#         invited[username] = int(timestamp)

# get scanned and invited players in record and clear scanned cache
with open("scanned.csv") as stream:
    reader = csv.reader(stream)
    scanned_header = next(reader)
    scanned_usernames = dict()
    scanned_player_ids = dict()
    for entry in reader:
        player = Candidate(*entry)
        if not player.invited and player.expiry <= now:
            continue
        scanned_usernames[player.username] = player
        if player.player_id:
            scanned_player_ids[player.player_id] = player

# get players in do_not_invite.csv
with open("do_not_invite.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    no_invite = set()
    for entry in reader:
        no_invite.add(entry[0])

# start session
session = requests.session()
session.headers.update(setup.headers())

# request timeout time when scanning individual players
timeout = 5

# check if victim club exists and get the victim club's admins
try:
    response = session.get(club.get_profile(), timeout=10)
except RequestException:
    raise SystemExit("request timed out when retrieving club profile")
if response.status_code != 200:
    raise SystemExit("cannot find club: {}".format(club.name))
admins = set(response.json()["admin"])

# get candidate players
try:
    response = session.get(club.get_members(), timeout=10)
except RequestException:
    raise SystemExit("request timed out when retrieving club member list")
if response.status_code != 200:
    raise SystemExit("cannot get member list: {}".format(response.status_code))
content: dict = response.json()
candidates = []
for category in content:
    for entry in content[category]:
        candidate = Candidate(username=entry["username"])
        if candidate.username in members:
            continue
        if candidate.username in admins:
            continue
        if candidate.username in no_invite:
            continue
        if candidate.username in scanned_usernames:
            if scanned_usernames[candidate.username].expiry > now:
                continue
            candidate = scanned_usernames[candidate.username]
        candidates.append(candidate)
if not candidates:
    raise SystemExit("no candidates to examine")

# make progress bars
candidates_bar = tqdm(total=len(candidates), desc="candidates", position=0, colour="blue")
invitables_bar = tqdm(total=target, desc="invitables", position=1, colour="yellow")

# start looting
invitables = []

try:
    for candidate in candidates:
        candidates_bar.update()

        # get player profile
        try:
            response = session.get(candidate.get_profile(), timeout=timeout)
        except RequestException:
            continue
        if response.status_code != 200:
            continue
        content = response.json()

        # make sure not to examine recently invited players
        # even if they've changed names
        if candidate.username not in scanned_usernames:
            candidate.player_id = content["player_id"]
            if candidate.player_id in scanned_player_ids:
                player = scanned_player_ids[candidate.player_id]
                scanned_usernames.pop(player.username)
                # update username and keep all other attributes
                player.username = candidate.username
                candidate = player
                scanned_usernames[candidate.username] = candidate
                if candidate.expiry > now:
                    continue

        # eliminate players offline for too long
        if now - content["last_online"] > setup.max_offline:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # get player clubs and eliminates players in too many clubs
        try:
            response = session.get(candidate.get_clubs(), timeout=timeout)
        except RequestException:
            continue
        if response.status_code != 200:
            continue
        if len(response.json()["clubs"]) > setup.max_clubs:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # get player stats
        try:
            response = session.get(candidate.get_stats(), timeout=timeout)
        except RequestException:
            continue
        if response.status_code != 200:
            continue
        content = response.json()

        # eliminate players who do not play daily
        if "chess_daily" not in content:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # eliminate players who move too slow
        if content["chess_daily"]["record"]["time_per_move"] > setup.max_move_time:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # eliminate players not in rating range
        if (
            content["chess_daily"]["last"]["rating"] < setup.min_elo or
            content["chess_daily"]["last"]["rating"] > setup.max_elo
        ):
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # eliminates players who lose or win too much
        wins = content["chess_daily"]["record"]["win"]
        losses = content["chess_daily"]["record"]["loss"]
        draws = content["chess_daily"]["record"]["draw"]
        # if "chess960_daily" in content:
        #     wins += content["chess960_daily"]["record"]["win"]
        #     losses += content["chess960_daily"]["record"]["loss"]
        #     draws += content["chess960_daily"]["record"]["draw"]
        score_rate = (wins + draws / 2) / (wins + losses + draws)
        if score_rate < setup.min_score_rate or score_rate > setup.max_score_rate:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # streamlines later procedures for players without any timeout
        no_timeout = content["chess_daily"]["record"]["timeout_percent"] == 0

        # get player ongoing games
        try:
            response = session.get(candidate.get_games(), timeout=timeout)
        except RequestException:
            continue
        if response.status_code != 200:
            continue
        games: list = response.json()["games"]

        # eliminate players with too many daily games ongoing
        if len(games) > setup.max_ongoing:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # eliminate players with too few club match games ongoing
        played = 0
        for game in games:
            if "match" in game:
                played += 1
        if played < setup.min_cm_ongoing:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
            continue

        # invite players with no timeout and enough club match games ongoing
        if no_timeout and played > setup.min_cm:
            invitables.append(candidate)
            invitables_bar.update()
            if len(invitables) >= target:
                break
            continue

        # this indicates whether something's wrong in the scanning process
        # in which case no record will be written for or against the player
        scan_complete = False

        # get player monthly archives
        for month in months:
            try:
                response = session.get(candidate.get_archive(month), timeout=timeout)
            except RequestException:
                break
            if response.status_code != 200:
                break
            games: list = response.json()["games"]

            # in the api, games are sorted by end time ascending
            # we traverse backwards, and once we see a game before 90 days
            # we can break out
            for game in games[::-1]:
                end_time: int = game["end_time"]
                if end_time < int(ninty.timestamp()):
                    no_timeout = scan_complete = True
                    break

                # invite players without timeout once they have enough club match games
                if "match" not in game:
                    continue
                played += 1
                if no_timeout:
                    if played >= setup.min_cm:
                        scan_complete = True
                        break
                    else:
                        continue

                # eliminate players with match timeout
                if game["white"]["username"].lower() == candidate.username:
                    colour = "white"
                else:
                    colour = "black"
                if game[colour]["result"] == "timeout":
                    scan_complete = True
                    candidate.expiry = end_time + setup.timeout_expiry
                    scanned_usernames[candidate.username] = candidate
                    break

            # if the player has already been found invitable or not,
            # no further monthly archives are needed
            if scan_complete:
                break

        # if all games have been scanned and the player has no timeout
        # in club match games, the player has no timeout in club match games
        else:
            no_timeout = scan_complete = True

        if not scan_complete:
            continue
        if not no_timeout:
            continue
        if played < setup.min_cm:
            candidate.expiry = now + setup.scanned_expiry
            scanned_usernames[candidate.username] = candidate
        else:
            invitables.append(candidate)
            invitables_bar.update()
            if len(invitables) >= target:
                break

    candidates_bar.close()
    invitables_bar.close()

# allows keyboard interrupt
except KeyboardInterrupt:
    candidates_bar.close()
    invitables_bar.close()
    # this is to avoid a bug where KeyboardInterrupt causes the first bar to duplicate
    # https://github.com/tqdm/tqdm/issues/1345
    invitables_bar.display("", -3)

session.close()

# with open("uninvitables.csv", "w") as stream:
#     writer = csv.writer(stream)
#     writer.writerow(header_uninvitables)
#     writer.writerows(sorted([[u, t] for u, t in uninvitables.items()]))

if invitables:
    print_bold("players invitable ({}):".format(len(invitables)))
    for candidate in invitables:
        print_bold(candidate.username, end=" ")
    print()
    confirmed = input("input 'Y' to invite these players: ")
    if confirmed == "Y":
        now = int(datetime.now(timezone.utc).timestamp())
        for candidate in invitables:
            candidate.expiry = now + setup.invited_expiry
            candidate.invited = True
            scanned_usernames[candidate.username] = candidate
        # with open("invited.csv", "w") as stream:
        #     writer = csv.writer(stream)
        #     writer.writerow(header_invited)
        #     writer.writerows(sorted([[u, t] for u, t in invited.items()]))
        print("{} players invited".format(len(invitables)))
    else:
        print("confirmation failed - please do it manually")
else:
    print("no invitable player found")

with open("scanned.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerow(scanned_header)
    for username in sorted(scanned_usernames.keys()):
        writer.writerow(scanned_usernames[username].to_csv_row())
