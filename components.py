def update_invited(usernames: list[str]):
    confirm = input("confirm inviting these players by typing 'Y': ")
    if confirm == 'Y':
        with open('invited.txt', 'r') as file:
            invited = file.read().strip(' \n').split('\n')
        invited += usernames
        invited.sort()
        with open('invited.txt', 'w') as file:
            file.write('\n'.join(invited))
        print(f'{len(usernames)} players invited')
        print(
            'The Great British Empire is an international club. We welcome chess players from all round the world, of all nationalities and all chess abilities.\n'
            'We are a competitive club, currently 10th worldwide on the club matches leaderboard, and we expect our members to play club matches whilst avoiding timeouts and fair play violations.\n'
            'We are also an active club in vote chess, which is a fun place for you to learn from your teammates’ ideas and to share your own.\n'
            'If you are interested in joining a multi-national club, and if you are keen on playing to win whilst making friends, then we are the club for you!\n'
        )
    else:
        print('confirmation failed. please update manually later.')

#
# def get_player_id(username: str) -> int:
#     username = username.strip(' /')
#     link = 'https://api.chess.com/pub/player/' + username
#     response = get(link)
#     info = response.json()
#     return info['player_id']
#
#
# def get_members(url: str) -> dict:
#     url = url.strip(' /')
#     link = 'https://api.chess.com/pub' + urlparse(url).path + '/members'
#     response = get(link)
#     updated = int(time())
#     members = response.json()
#     members['members'] = []
#     members['updated'] = updated
#     for category in ('weekly', 'monthly', 'all_time'):
#         members['members'] += members.pop(category)
#     return members
#
#
# def get_player_ids(members: dict) -> dict:
#     with IncrementalBar('Progress', max=len(members['members'])) as bar:
#         for member in members['members']:
#             member['player_id'] = get_player_id(member['username'])
#             bar.next()
#     return members
