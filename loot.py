import json
from time import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
from progress.bar import IncrementalBar
from components import *

# constraints
target = int(input('number of players to invite: '))
enter_cache = True
min_tm_played = 12  # int(input('minimum number of team match games in last 90 days: '))
min_tm_ongoing = 2  # int(input('minimum number of ongoing games: '))
max_ongoing = 100  # int(input('maximum number of ongoing games: '))
max_clubs = 30  # int(input('maximum number of clubs: '))
min_rating = 1000  # int(input('minimum rating (inclusive): '))
max_rating = 2500  # int(input('maximum rating (inclusive): '))
# min_win_rate = 0.4  # int(input('minimum win rate: '))
# max_win_rate = 0.8  # int(input('maximum win rate: '))
min_score_rate = 0.45
max_score_rate = 0.85
max_time_per_move = timedelta(hours=18)
avoid_admins = True

# find yyyy/mm
current_datetime = datetime.today()
archive_datetime = current_datetime - timedelta(days=90)
months = []
while archive_datetime <= current_datetime:
    months.append('{}/{:>02}'.format(archive_datetime.year, archive_datetime.month))
    archive_datetime += relativedelta(months=+1)
months.reverse()
archive_datetime = current_datetime - timedelta(days=90)

# clear cache
try:
    with open('scanned.json', 'r') as scanned_json:
        scanned = json.load(scanned_json)
    for key in list(scanned.keys()):
        if scanned[key] <= current_datetime.timestamp():
            del scanned[key]
    with open('scanned.json', 'w') as scanned_json:
        json.dump(scanned, scanned_json)
except json.JSONDecodeError:
    scanned = {}


# start looting
club_name = input('enter club name (as in url): ').strip(' /')
start = time()

# get the victim club's admins
response = requests.get(f'https://api.chess.com/pub/club/{club_name}', timeout=10)
if response.status_code != 200:
    raise Exception('invalid url or connection error')
club_admins = set(response.json()['admin'])

# get players to examine
response = requests.get(f'https://api.chess.com/pub/club/{club_name}/members', timeout=10)
if response.status_code != 200:
    raise Exception('connection error')
candidates = []
with open('membership.json') as membership_json:
    membership = json.load(membership_json)
with open('lost_members.json') as lost_members_json:
    lost_members = json.load(lost_members_json)
with open('invited.txt') as invited_txt:
    invited = set(invited_txt.read().strip(' \n').split('\n'))
for category in ('weekly', 'monthly', 'all_time'):
    for member in response.json()[category]:
        # skip existing members
        if member['username'].lower() in membership:
            continue
        # skip former members
        if member['username'].lower() in lost_members:
            continue
        # skip already invited players
        if member['username'].lower() in invited:
            continue
        # skip cached uninvitable players
        if member['username'].lower() in scanned:
            continue
        # skip admins
        if avoid_admins:
            if f'https://api.chess.com/pub/player/{member["username"].lower()}' in club_admins:
                continue
        candidates.append(member['username'].lower())


try:
    # examine players
    with IncrementalBar('processed', max=len(candidates)) as candidates_bar:
        invitable = []
        for player in candidates:
            candidates_bar.next()

            # check number of clubs
            try:
                response = requests.get(f'https://api.chess.com/pub/player/{player}/clubs', timeout=10)
            except requests.exceptions.RequestException:
                continue
            if response.status_code != 200:
                continue
            if len(response.json()['clubs']) > max_clubs:
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # get player stats
            try:
                response = requests.get(f'https://api.chess.com/pub/player/{player}/stats', timeout=10)
            except requests.exceptions.RequestException:
                continue
            if response.status_code != 200:
                continue

            # eliminates players who don't play daily
            if 'chess_daily' not in response.json():
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # eliminates players who move too slow
            if timedelta(seconds=response.json()['chess_daily']['record']['time_per_move']) > max_time_per_move:
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # eliminates players not in rating range
            if (
                response.json()['chess_daily']['last']['rating'] < min_rating or
                response.json()['chess_daily']['last']['rating'] > max_rating
            ):
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # eliminates players who lose or win too much
            wins = response.json()['chess_daily']['record']['win']
            losses = response.json()['chess_daily']['record']['loss']
            draws = response.json()['chess_daily']['record']['draw']
            if 'chess960_daily' in response.json():
                wins += response.json()['chess960_daily']['record']['win']
                losses += response.json()['chess960_daily']['record']['loss']
                draws += response.json()['chess960_daily']['record']['draw']
            score_rate = (wins + draws / 2) / (wins + losses + draws)
            if score_rate < min_score_rate or score_rate > max_score_rate:
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # streamlines later procedures for players without any timeout
            no_timeout = response.json()['chess_daily']['record']['timeout_percent'] == 0

            # get player ongoing games
            try:
                response = requests.get(f'https://api.chess.com/pub/player/{player}/games', timeout=10)
            except requests.exceptions.RequestException:
                continue
            if response.status_code != 200:
                continue

            # eliminates players with too many games ongoing
            if len(response.json()['games']) > max_ongoing:
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # eliminates players with too few team match games ongoing
            tm_played = 0
            for game in response.json()['games']:
                if 'match' in game:
                    tm_played += 1
            if tm_played < min_tm_ongoing:
                if enter_cache:
                    scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
                continue

            # invites players without timeouts and with enough team match games ongoing
            if no_timeout and tm_played >= min_tm_played:
                invitable.append(player)
                if len(invitable) >= target:
                    break
                continue

            # get player monthly game archive
            is_invitable = True
            for month in months:
                try:
                    response = requests.get(f'https://api.chess.com/pub/player/{player}/games/{month}', timeout=10)
                except requests.exceptions.RequestException:
                    is_invitable = False
                    break
                if response.status_code != 200:
                    is_invitable = False
                    break
                response.json()['games'].reverse()

                # check each game
                for game in response.json()['games']:
                    if 'match' in game:
                        if datetime.fromtimestamp(game['end_time']) <= archive_datetime:
                            continue
                        tm_played += 1

                        # invite players without timeout and with enough team match games played
                        if no_timeout:
                            if tm_played >= min_tm_played:
                                break

                        # eliminate players with team match timeouts
                        else:
                            if game['white']['username'].lower() == player:
                                if game['white']['result'] == 'timeout':
                                    is_invitable = False
                                    if enter_cache:
                                        scanned[player] = game['end_time'] + int(timedelta(days=90).total_seconds())
                                    break
                            else:
                                if game['black']['result'] == 'timeout':
                                    is_invitable = False
                                    if enter_cache:
                                        scanned[player] = game['end_time'] + int(timedelta(days=90).total_seconds())
                                    break

                # check if further scan is needed
                if not is_invitable:
                    break
                if no_timeout and tm_played >= min_tm_played:
                    break

            # invite players without timeout who played enough games
            if is_invitable:
                if tm_played >= min_tm_played:
                    invitable.append(player)
                    if len(invitable) >= target:
                        break

                # eliminate players without enough team match games
                else:
                    if enter_cache:
                        scanned[player] = int(current_datetime.timestamp() + timedelta(days=30).total_seconds())
except KeyboardInterrupt:
    pass

end = time()

# update cache
if enter_cache:
    scanned = dict(sorted(scanned.items()))
    with open('scanned.json', 'w') as scanned_json:
        json.dump(scanned, scanned_json)

# output
print(f'players invitable ({len(invitable)}):')
if invitable:
    for player in invitable:
        print(player, end=' ')
else:
    print('(none)')
print(f'\nruntime: {timedelta(seconds=int(end - start))}')
if invitable:
    update_invited(invitable)
