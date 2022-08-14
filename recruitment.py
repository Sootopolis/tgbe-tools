import requests
from components import Setup, Member, Club, print_bold
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import csv
from tqdm import tqdm


# load setup
setup = Setup()
setup.load()

# set target number and victim club
target = int(input("number of players to invite: "))
club = Club(input("enter club name as in url; leave empty to quit: ").strip())
if not club.name:
    raise SystemExit("club name not provided")

# find yyyy/mm
now = datetime.now(timezone.utc)
now_timestamp = int(now.timestamp())
ninty = now - timedelta(days=90)
months = []
while ninty <= now:
    months.append("{}/{:>02}".format(ninty.year, ninty.month))
    ninty += relativedelta(months=+1)
months.reverse()
ninty = now - timedelta(days=90)

# get and clear uninvitable cache
with open("uninvitables.csv") as stream:
    reader = csv.reader(stream)
    header_uninvitables = next(reader)
    uninvitables = dict()
    if setup.clear_uninvitable_cache:
        for username, timestamp in reader:
            if int(timestamp) <= now_timestamp:
                continue
            uninvitables[username] = int(timestamp)
    else:
        for username, timestamp in reader:
            uninvitables[username] = int(timestamp)

# get members and former members in record
with open("members.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    members = set()
    for entry in reader:
        members.add(entry[0])

# get invited players in record
with open("invited.csv") as stream:
    reader = csv.reader(stream)
    header_invited = next(reader)
    invited = dict()
    for username, timestamp in reader:
        invited[username] = int(timestamp)

# get players in do_not_invite.csv
with open("do_not_invite.csv") as stream:
    reader = csv.reader(stream)
    next(reader)
    no_invite = set()
    for entry in reader:
        no_invite.add(entry[0])

# start session
session = requests.session()
session.headers.update({
    "Accept": "application/json",
    "from": setup.email
})

# check if victim club exists and get the victim club's admins
response = session.get(club.get_profile())
if response.status_code != 200:
    raise SystemExit("cannot find club: {}".format(club.name))
content = response.json()
admins = set(content["admin"])

# get candidate players
response = session.get(club.get_members())
if response.status_code != 200:
    raise SystemExit("failed to get member list - {}".format(response.status_code))
content = response.json()
candidates = []
for category in content:
    for entry in content[category]:
        username: str = entry["username"].lower()
        if (
            username in members or
            username in uninvitables or
            username in admins or
            username in no_invite or
            (
                    username in invited and
                    invited[username] + setup.invited_expiry >= now_timestamp
            )
        ):
            continue
        candidates.append(username)
if not candidates:
    raise SystemExit("no players to scan")

# make progress bars
candidates_bar = tqdm(total=len(candidates), desc="candidates", position=0, colour="blue")
invitables_bar = tqdm(total=target, desc="invitables", position=1, colour="yellow")

# start looting
invitables = []

try:
    for username in candidates:
        player = Member(username)
        candidates_bar.update()

        # get player profile and eliminate players offline for too long
        response = session.get(player.get_profile())
        if response.status_code != 200:
            continue
        if now_timestamp - response.json()["last_online"] > setup.max_offline:
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # get player clubs and eliminates players in too many clubs
        response = session.get(player.get_clubs())
        if response.status_code != 200:
            continue
        if len(response.json()["clubs"]) > setup.max_clubs:
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # get player stats
        response = session.get(player.get_stats())
        if response.status_code != 200:
            continue
        content = response.json()

        # eliminate players who do not play daily
        if "chess_daily" not in content:
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # eliminate players who move too slow
        if content["chess_daily"]["record"]["time_per_move"] > setup.max_move_time:
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # eliminate players not in rating range
        if (
            content["chess_daily"]["last"]["rating"] < setup.min_elo or
            content["chess_daily"]["last"]["rating"] > setup.max_elo
        ):
            uninvitables[username] = now_timestamp + setup.scanned_expiry
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
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # streamlines later procedures for players without any timeout
        no_timeout = content["chess_daily"]["record"]["timeout_percent"] == 0

        # get player ongoing games
        response = session.get(player.get_games())
        if response.status_code != 200:
            continue
        games: list = response.json()["games"]

        # eliminate players with too many daily games ongoing
        if len(games) > setup.max_ongoing:
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # eliminate players with too few club match games ongoing
        played = 0
        for game in games:
            if "match" in game:
                played += 1
        if played < setup.min_cm_ongoing:
            uninvitables[username] = now_timestamp + setup.scanned_expiry
            continue

        # invite players with no timeout and enough club match games ongoing
        if no_timeout and played > setup.min_cm:
            invitables.append(username)
            invitables_bar.update()
            if len(invitables) >= target:
                break
            continue

        # this indicates whether something's wrong in the scanning process
        # in which case no record will be written for or against the player
        scan_complete = False

        # get player monthly archives
        for month in months:
            response = session.get(player.get_archive(month))
            if response.status_code != 200:
                break
            games: list = response.json()["games"]

            # in the api, games are sorted by end time ascending
            # we traverse backwards, and once we see a game before 90 days
            # we can break out
            for game in games[::-1]:
                game: dict
                if game["end_time"] < int(ninty.timestamp()):
                    no_timeout = scan_complete = True
                    break

                # invite players without timeout once they have enough club match games
                if "match" not in game:
                    continue
                played += 1
                if no_timeout:
                    if played > setup.min_cm:
                        scan_complete = True
                        break
                    else:
                        continue

                if game["white"]["username"].lower() == username:
                    colour = "white"
                else:
                    colour = "black"
                if game[colour]["result"] == "timeout":
                    scan_complete = True
                    break

            # if the player has already been found invitable or not,
            # no further monthly archives are needed
            if scan_complete:
                break

        # if all games have been scanned and the player has no timeout
        # in club match games, the player has no timeout in club match games
        else:
            no_timeout = scan_complete = True

        if scan_complete:
            if not no_timeout:
                uninvitables[username] = now_timestamp + setup.timeout_expiry
            elif played < setup.min_cm:
                uninvitables[username] = now_timestamp + setup.scanned_expiry
            else:
                invitables.append(username)
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

with open("uninvitables.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerow(header_uninvitables)
    writer.writerows(sorted([[u, t] for u, t in uninvitables.items()]))

if invitables:
    print_bold("players invitable ({}):".format(len(invitables)))
    for username in invitables:
        print_bold(username, end=" ")
    print()
    confirmed = input("input 'Y' to invite these players: ")
    if confirmed == "Y":
        timestamp = int(datetime.now(timezone.utc).timestamp())
        for username in invitables:
            invited[username] = timestamp
        with open("invited.csv", "w") as stream:
            writer = csv.writer(stream)
            writer.writerow(header_invited)
            writer.writerows(sorted([[u, t] for u, t in invited.items()]))
        print("{} players invited".format(len(invitables)))
    else:
        print("confirmation failed - please do it manually")
else:
    print("no invitable player found")
