from requests import get
from urllib.parse import urlparse
from time import time, sleep  # , gmtime, strftime
from pprint import pprint
from progress.bar import IncrementalBar


def get_player_id(username: str) -> int:
    username = username.strip(' /')
    link = 'https://api.chess.com/pub/player/' + username
    response = get(link)
    info = response.json()
    return info['player_id']


def get_members(url: str) -> dict:
    url = url.strip(' /')
    link = 'https://api.chess.com/pub' + urlparse(url).path + '/members'
    response = get(link)
    updated = int(time())
    members = response.json()
    members['members'] = []
    members['updated'] = updated
    for category in ('weekly', 'monthly', 'all_time'):
        members['members'] += members.pop(category)
    return members


def get_player_ids(members: dict) -> dict:
    with IncrementalBar('Progress', max=len(members['members'])) as bar:
        for member in members['members']:
            member['player_id'] = get_player_id(member['username'])
            bar.next()
    return members


print(get_player_ids(get_members('https://www.chess.com/club/tgbe-office-for-planning-and-preparation')))
