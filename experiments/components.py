import csv
import json
from json import JSONDecodeError
# from collections import namedtuple
from pprint import pp


# Parameter = namedtuple("Parameter", ["default", "desc"])


class Setup:

    # initialise each parameter to a tuple containing its default value and description
    # they will later be overwritten with either the default values or user inputs
    # it may not be optimal practice, but i find it easier to hard coded them here
    # than to put them in a file that can be easily changed
    def __init__(self):
        self.club = (
            "",
            "name of your club as in url"
        )
        self.email = (
            "",
            "your email address (so that chess.com can email you regarding your api usage)"
        )
        self.username = (
            "",
            "your chess.com username (so that chess.com can message you regarding your api usage)"
        )
        self.avoid_admins = (
            1,
            "AVOID inviting admins? (1 = true, 0 = false)"
        )
        self.allow_re_invitations = (
            1,
            "allow re-invitation? (1 = true, 0 = false)"
        )
        self.clear_uninvitable_cache = (
            1,
            "clear expired uninvitable cache before looting? (1 = true, 0 = False)"
        )
        self.re_invite = (
            180,
            "days after last invitation that re-invitation is allowed (only relevant if re-invitation is allowed)"
        )
        self.uninvitable_exp = (
            30,
            "days after a non-timeout uninvitable record that a player can be assessed again"
        )
        self.timeout_exp = (
            90,
            "days after most recent timeout that a player can be assessed again"
        )
        self.max_clubs = (
            30,
            "maximum number of joined clubs for a player to be assessed"
        )
        self.max_hours_per_move = (
            18,
            "maximum hours per move in daily chess for a player to be assessed"
        )
        self.max_hours_offline = (
            48,
            "maximum hours since last login for a player to be assessed"
        )
        self.min_cm = (
            12,
            "minimum club matches finished/ongoing for a player to be assessed"
        )
        self.min_cm_ongoing = (
            2,
            "minimum club matches ongoing for a player to be assessed"
        )
        self.max_ongoing = (
            100,
            "maximum daily chess games ongoing for a player to be assessed"
        )
        self.min_elo = (
            1000,
            "minimum elo points for a player to be assessed"
        )
        self.max_elo = (
            2300,
            "maximum elo points for a player to be assessed"
        )
        self.min_score_rate = (
            0.45,
            "minimum score rate for a player to be assessed"
        )
        self.max_score_rate = (
            0.85,
            "maximum score rate for a player to be assessed"
        )

    # a method to overwrite attributes with default values or user inputs
    def setup(self):

        def input_default(parameter):
            default, desc = getattr(self, parameter)
            t = type(default)
            print(desc)
            value = input("value [default = {}]: ".format(default))
            if value:
                setattr(self, parameter, t(value))
            else:
                setattr(self, parameter, default)

        parameters = list(vars(self).keys())
        n = len(parameters)
        print("for each parameter, enter without input to use default value")
        for i in range(3):
            print("\n{} / n".format(i + 1))
            input_default(parameters[i])
        print("\nthe remaining parameters are relevant to loot.py only")
        for i in range(3, 17):
            print("\n{} / n".format(i + 1))
            input_default(parameters[i])
        print("\nfor the next 2 parameters:")
        print("score rate = (wins + 0.5 * draws) / games")
        for i in range(17, 19):
            print("\n{} / n".format(i + 1))
            input_default(parameters[i])

        # store setup in setup.json
        with open("setup.json", "w") as stream:
            json.dump(vars(self), stream)
        print("\nsetup updated")


# use this to import the setup
def get_setup() -> Setup:
    with open("setup.json") as stream:
        try:
            data = json.load(stream)
        except JSONDecodeError:
            raise SystemExit("problem with setup.json - try running setup.py to fix this")
    setup = Setup()
    for key, value in data.items():
        setattr(setup, key, value)
    return setup


def generate_headers(username: str = "", email: str = "") -> dict:
    headers = {"Accept": "application/json"}
    if username:
        headers["User-Agent"] = username
    if email:
        headers["From"] = email
    return headers


def print_bold(s: str, end="\n", sep=" "):
    print("\033[1m" + s + "\033[0m", end=end, sep=sep)


def type_names() -> list[str]:
    names = []
    print("input names:")
    while True:
        name = input().lower().split()
        if name:
            names += name
        else:
            break
    return names
