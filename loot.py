import json
from time import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
from progress.bar import IncrementalBar
from components import *

target = int(input('number of players to invite: '))
club_name = input('enter club name (as in url; leave empty to quit): ').strip(' /')
if not club_name:
    quit()

# constraints
enter_cache = True
clear_cache = True
min_cm_played = 12  # int(input('minimum number of team match games in last 90 days: '))
min_cm_ongoing = 2  # int(input('minimum number of ongoing games: '))
max_ongoing = 100  # int(input('maximum number of ongoing games: '))
max_clubs = 32  # int(input('maximum number of clubs: '))
min_rating = 1000  # int(input('minimum rating (inclusive): '))
max_rating = 2300  # int(input('maximum rating (inclusive): '))
# min_win_rate = 0.4  # int(input('minimum win rate: '))
# max_win_rate = 0.8  # int(input('maximum win rate: '))
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
    months.append('{}/{:>02}'.format(archive_datetime.year, archive_datetime.month))
    archive_datetime += relativedelta(months=+1)
months.reverse()
archive_datetime = current_datetime - timedelta(days=90)

# clear cache and get scanned players
try:
    with open('scanned_players.json', 'r') as scanned_json:
        scanned = json.load(scanned_json)
    if clear_cache:
        for key in list(scanned.keys()):
            if scanned[key] <= start:
                del scanned[key]
except json.JSONDecodeError:
    scanned = {}

# start looting
with requests.session() as session:

    # check if victim club exists and get the victim club's admins
    response = session.get(f'https://api.chess.com/pub/club/{club_name}', timeout=5)
    if response.status_code != 200:
        print('connection error')
        quit()
    content = response.json()
    if content.get('code', 1) == 0:
        print('club does not exist')
        quit()
    club_admins = set(content['admin'])

    # get players to examine
    response = session.get(f'https://api.chess.com/pub/club/{club_name}/members', timeout=5)
    if response.status_code != 200:
        print('connection error')
        quit()
    content = response.json()
    candidates = []
    with open('membership.json') as membership_json:
        membership = json.load(membership_json)
    with open('lost_members.json') as lost_members_json:
        lost_members = json.load(lost_members_json)
    with open('invited.txt') as invited_txt:
        invited = set(invited_txt.read().strip(' \n').split('\n'))
    for category in ('weekly', 'monthly', 'all_time'):
        for member in content[category]:
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

                # get player profile
                try:
                    response = session.get(f'https://api.chess.com/pub/player/{player}', timeout=5)
                except requests.exceptions.RequestException:
                    continue
                if response.status_code != 200:
                    continue
                content = response.json()

                # eliminates players offline for too long
                if current_datetime - datetime.fromtimestamp(content['last_online']) > max_offline:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # get player clubs
                try:
                    response = session.get(f'https://api.chess.com/pub/player/{player}/clubs', timeout=5)
                except requests.exceptions.RequestException:
                    continue
                if response.status_code != 200:
                    continue
                content = response.json()

                # eliminates players with too many clubs
                if len(content['clubs']) > max_clubs:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # get player stats
                try:
                    response = session.get(f'https://api.chess.com/pub/player/{player}/stats', timeout=5)
                except requests.exceptions.RequestException:
                    continue
                if response.status_code != 200:
                    continue
                content = response.json()

                # eliminates players who don't play daily
                if 'chess_daily' not in content:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # eliminates players who move too slow
                if timedelta(seconds=content['chess_daily']['record']['time_per_move']) > max_time_per_move:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # eliminates players not in rating range
                if (
                    content['chess_daily']['last']['rating'] < min_rating or
                    content['chess_daily']['last']['rating'] > max_rating
                ):
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # eliminates players who lose or win too much
                wins = content['chess_daily']['record']['win']
                losses = content['chess_daily']['record']['loss']
                draws = content['chess_daily']['record']['draw']
                if 'chess960_daily' in content:
                    wins += content['chess960_daily']['record']['win']
                    losses += content['chess960_daily']['record']['loss']
                    draws += content['chess960_daily']['record']['draw']
                score_rate = (wins + draws / 2) / (wins + losses + draws)
                if score_rate < min_score_rate or score_rate > max_score_rate:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # streamlines later procedures for players without any timeout
                no_timeout = content['chess_daily']['record']['timeout_percent'] == 0

                # get player ongoing games
                try:
                    response = session.get(f'https://api.chess.com/pub/player/{player}/games', timeout=5)
                except requests.exceptions.RequestException:
                    continue
                if response.status_code != 200:
                    continue
                content = response.json()

                # eliminates players with too many games ongoing
                if len(content['games']) > max_ongoing:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # eliminates players with too few team match games ongoing
                cm_played = 0
                for game in content['games']:
                    if 'match' in game:
                        cm_played += 1
                if cm_played < min_cm_ongoing:
                    if enter_cache:
                        scanned[player] = int(start + timedelta(days=30).total_seconds())
                    continue

                # invites players without timeouts and with enough team match games ongoing
                if no_timeout and cm_played >= min_cm_played:
                    invitable.append(player)
                    if len(invitable) >= target:
                        break
                    continue

                # get player monthly game archive
                is_invitable = True
                for month in months:
                    try:
                        response = session.get(f'https://api.chess.com/pub/player/{player}/games/{month}', timeout=5)
                    except requests.exceptions.RequestException:
                        is_invitable = False
                        break
                    if response.status_code != 200:
                        is_invitable = False
                        break
                    content = response.json()
                    content['games'].reverse()

                    # check each game
                    for game in content['games']:
                        if 'match' in game:
                            if datetime.fromtimestamp(game['end_time']) <= archive_datetime:
                                continue
                            cm_played += 1

                            # invite players without timeout and with enough team match games played
                            if no_timeout:
                                if cm_played >= min_cm_played:
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
                    if no_timeout and cm_played >= min_cm_played:
                        break

                # invite players without timeout who played enough games
                if is_invitable:
                    if cm_played >= min_cm_played:
                        invitable.append(player)
                        if len(invitable) >= target:
                            break

                    # eliminate players without enough team match games
                    else:
                        if enter_cache:
                            scanned[player] = int(start + timedelta(days=30).total_seconds())

    except KeyboardInterrupt:
        pass

end = int(time())

# update cache
if enter_cache:
    # scanned = dict(sorted(scanned.items()))
    with open('scanned_players.json', 'w') as scanned_json:
        json.dump(scanned, scanned_json, sort_keys=True, indent=2)

# output
print(f'players invitable ({len(invitable)}):')
if invitable:
    for player in invitable:
        print(player, end=' ')
else:
    print('(none)', end=' ')
print(f'\nruntime: {timedelta(seconds=(end - start))}')
if invitable:
    update_invited(invitable)
