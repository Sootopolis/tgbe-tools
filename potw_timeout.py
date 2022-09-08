import csv
from components import Setup, Member, Board
from datetime import datetime, timedelta

# find last and this thursdays


# load setup
setup = Setup()
setup.load()

# result codes
W = {"win"}
D = {"agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"}
L = {"resigned", "checkmated", "timeout", "lose"}

# load members
members = dict()

with open("members.csv") as stream:
    reader = csv.reader(stream)
    header_members = next(reader)
    for entry in reader:
        member = Member(*entry)

with open("potw.csv") as stream:
    reader = csv.reader(stream)
    header_potw = next(stream)
    for entry in reader:
        username = entry[0]
        try:
            assert username in members
        except AssertionError:
            raise SystemExit(f"loading stats - {username} is not in members")
        member: Member = members[username]
        member.load_stats(*entry[1:])

matches = dict()
# load boards in local record
with open("boards.csv") as stream:
    reader = csv.reader(stream)
    header_boards = next(reader)
    for entry in reader:
        board = Board(*entry)

