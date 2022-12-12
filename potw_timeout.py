import csv
from components import Setup, Member, Board
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta, TH


# get this and last checkpoints
def get_thursdays(dt: datetime) -> tuple[datetime, datetime]:
    # if it's thursday before 10:00, pretend it's wednesday
    if (
        dt.weekday() == 3 and
        dt.hour < 10 or
        dt.hour == 10 and not (dt.minute == dt.second == dt.microsecond == 0)
    ):
        dt += timedelta(days=-1)
    # get datetime of this and last thursday 10:00
    this_cp = dt + relativedelta(weekday=TH(-1), hour=10, minute=0, second=0, microsecond=0)
    last_cp = dt + relativedelta(weekday=TH(-2), hour=10, minute=0, second=0, microsecond=0)
    return this_cp, last_cp


# get current datetime
now = datetime.now(tz=timezone.utc)

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
        match_id = board.match_id
        if match_id not in matches:
            matches[match_id] = [board]
        else:
            matches[match_id].append(board)


