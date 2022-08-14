from components import Setup, Member, Club, ClubMatch, print_bold
import requests
import csv
from tqdm import tqdm

# load setup
setup = Setup()
setup.load()
result_codes = {
    "W": ["win"],
    "D": [
        "agreed",
        "repetition",
        "stalemate",
        "insufficient",
        "50move",
        "timevsinsufficient"
    ],
    "L": [
        "resigned",
        "checkmated",
        "timeout",
        "lose"
    ]
}

# load boards in local record
with open("matches.csv") as stream:
    reader = csv.reader(stream)
    header = next(reader)
    registered = dict()
    in_progress = dict()
    for match_id, started, boards, end_time in reader:
        pass
