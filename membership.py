import requests
import json
from json.decoder import JSONDecodeError
from datetime import datetime


url = 'https://api.chess.com/pub/club/the-great-british-empire/members'
response = requests.get(url)

if response.status_code == 200:

    new_members = {}
    for category in ('weekly', 'monthly', 'all_time'):
        for entry in response.json()[category]:
            new_members[entry['username']] = entry['joined']
    with open('membership.json', 'r') as file:
        try:
            old_members = json.load(file)
        except JSONDecodeError:
            old_members = {}
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
        print('arrivals:')
        for i in range(len(came)):
            print(came[i][0], datetime.fromtimestamp(came[i][1]))

    if went:
        print('departures:')
        for i in range(len(went)):
            print(went[i][0])
        with open('lost_members.json', 'r') as lost_members_json:
            try:
                lost_members = json.load(lost_members_json)
            except JSONDecodeError:
                lost_members = {}
        with open('lost_members.json', 'w') as lost_members_json:
            for i in range(len(went)):
                lost_members[went[i][0]] = went[i][1]
            lost_members = dict(sorted(lost_members.items()))
            json.dump(lost_members, lost_members_json)

    if changed:
        print('NAME CHANGES:')
        for i in range(len(changed)):
            print(f'{changed[i][0]} is now known as {changed[i][1]}')

    new_members = dict(sorted(new_members.items()))
    with open('membership.json', 'w') as file:
        json.dump(new_members, file)
    print(f'total members: {len(new_members)}')

else:
    print(f'Error: {response.status_code}')
