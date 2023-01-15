import csv
import requests
from components import Setup

setup = Setup()
setup.load()
session = requests.session()
session.headers.update(setup.headers())

usernames = dict()
with open("do_not_invite.csv") as stream:
    reader = csv.reader(stream)
    header = next(reader)
    for entry in reader:
        usernames[entry[0]] = entry[1:]

while True:
    username = input("input username, enter blank to quit: ").lower()
    if not username:
        break
    content = session.get("https://api.chess.com/pub/player/{}".format(username)).json()
    if "code" in content:
        print("username does not exist")
    else:
        player_id = content["player_id"]
        is_nice = int(bool(input("is the player 'nice'? blank for false, anything for true: ")))
        usernames[username] = [player_id, is_nice]

with open("do_not_invite.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerow(header)
    for username in sorted(usernames.keys()):
        writer.writerow([username] + usernames[username])
