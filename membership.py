import requests
import json
from json.decoder import JSONDecodeError
from time import time, gmtime, strftime
from datetime import datetime, timedelta


url = 'https://api.chess.com/pub/club/the-great-british-empire/members'
response = requests.get(url)

if response.status_code == 200:

    updated = int(time())
    data = response.json()
    new_members = {}
    for category in ('weekly', 'monthly', 'all_time'):
        for entry in data[category]:
            new_members[entry['username']] = entry['joined']

    try:
        with open('membership.json', 'r') as file:
            old_members = json.load(file)
            came = list(new_members.items() - old_members.items())
            went = list(old_members.items() - new_members.items())
            came.sort(key=lambda x: x[1])
            went.sort(key=lambda x: x[1])
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
                    print(came[i][0], strftime("%X %A %d %B %Y %Z", gmtime(came[i][1])), end=' ')
                    print()
            if went:
                print('departures:')
                for i in range(len(went)):
                    print(went[i][0], strftime("%X %A %d %B %Y %Z", gmtime(went[i][1])), end=' ')
                    print()
                with open('lost_members.json', 'r') as lost_members:
                    try:
                        lost_members_json = json.load(lost_members)
                    except JSONDecodeError:
                        lost_members_json = {}
                with open('lost_members.json', 'w') as lost_members:
                    for i in range(len(went)):
                        lost_members_json[went[i][0]] = went[i][1]
                    json.dump(lost_members_json, lost_members)

            if changed:
                print('name changes:')
                for i in range(len(changed)):
                    print(f'{changed[i][0]} is now known as {changed[i][1]}')
    except FileNotFoundError:
        pass

    with open('membership.json', 'w') as file:
        json.dump(new_members, file)
    # pprint(new_members)
    print(f'total members: {len(new_members)}')
    print(f'last update: {strftime("%X %A %d %B %Y %Z", gmtime(updated))}')

else:
    print(f'Error: {response.status_code}')
