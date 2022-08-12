import json
from json import JSONDecodeError
from collections import deque
from datetime import datetime, timedelta, timezone


class Player:

    def __init__(
            self,
            username: str,
            player_id: int = 0,
            timestamp: int = 0,
            is_closed: bool = False,
            is_former: bool = False
    ):
        self.username = username.lower()
        self.player_id = player_id
        self.timestamp = timestamp
        self.is_closed = is_closed
        self.is_former = is_former
        # self.__W = 0
        # self.__D = 0
        # self.__L = 0
        # self.__last_activity = 0
        # self.__last_point = 0

    def get_profile(self):
        return "https://api.chess.com/pub/player/{}".format(self.username)

    def get_page(self):
        return "https://www.chess.com/member/{}".format(self.username)

    def get_clubs(self):
        return "https://api.chess.com/pub/player/{}/clubs".format(self.username)

    def get_stats(self):
        return "https://api.chess.com/pub/player/{}/stats".format(self.username)

    def get_games(self):
        return "https://api.chess.com/pub/player/{}/games".format(self.username)

    def get_archive(self, month: str):
        return "https://api.chess.com/pub/player/{}/games/{}".format(self.username, month)

    # def win(self, timestamp: int = 0):
    #     self.__W += 1
    #     if timestamp:
    #         self.__last_point = max(self.__last_point, timestamp)
    #         self.__last_activity = max(self.__last_activity, timestamp)

    # def draw(self, timestamp: int = 0):
    #     self.__D += 1
    #     if timestamp:
    #         self.__last_point = max(self.__last_point, timestamp)
    #         self.__last_activity = max(self.__last_activity, timestamp)

    # def lose(self, timestamp: int = 0):
    #     self.__L += 1
    #     if timestamp:
    #         self.__last_activity = max(self.__last_activity, timestamp)

    def __repr__(self):
        return self.username

    # two Player objects are considered equal if they share the same username,
    # player_id (if both are specified), and timestamp (if both are specified)
    def __eq__(self, other):
        if not isinstance(other, Player):
            raise TypeError("comparing a Player instance with a non-Player instance")
        if self.username != other.username:
            return False
        if (
                self.player_id and
                other.player_id and
                self.player_id != other.player_id
        ):
            return False
        if (
                self.timestamp and
                other.timestamp and
                self.timestamp != other.timestamp
        ):
            return False
        return True

    # def __lt__(self, other):
    #     if not isinstance(other, Player):
    #         raise TypeError("comparing a Player instance with a non-Player instance")
    #     return self.username < other.username

    # def __le__(self, other):
    #     if not isinstance(other, Player):
    #         raise TypeError("comparing a Player instance with a non-Player instance")
    #     return self.username <= other.username

    # def __gt__(self, other):
    #     if not isinstance(other, Player):
    #         raise TypeError("comparing a Player instance with a non-Player instance")
    #     return self.username > other.username

    # def __ge__(self, other):
    #     if not isinstance(other, Player):
    #         raise TypeError("comparing a Player instance with a non-Player instance")
    #     return self.username >= other.username

    # define hash so that Player objects can be in sets
    # usernames are not unique identifiers
    # but is the only attribute that a Player is guaranteed to have
    # as new members will lack player_id for the sake of runtime
    def __hash__(self):
        return hash(self.username)


class Setup:

    club = ""
    email = ""
    username = ""
    avoid_admins = 1
    allow_re_invitations = 1
    clear_uninvitable_cache = 1
    re_invite = 180
    uninvitable_exp = 30
    timeout_exp = 90
    max_clubs = 30
    max_hours_per_move = 18
    max_hours_offline = 48
    min_cm = 12
    min_cm_ongoing = 2
    max_ongoing = 100
    min_elo = 1000
    max_elo = 2300
    min_score_rate = 0.45
    max_score_rate = 0.85

    # a method to overwrite attributes with default values or user inputs
    def customise_setup(self):
        def input_default(parameter):
            default = getattr(self, parameter)
            t = type(default)
            value = input("{} [default = {}]: ".format(parameter, default))
            if value:
                if isinstance(default, bool):
                    setattr(self, parameter, bool(int(value)))
                else:
                    setattr(self, parameter, t(value))
            else:
                setattr(self, parameter, default)

        parameters = list(vars(self).keys())
        n = len(parameters)
        print_bold("for each parameter, enter without input to use default value")
        for i in range(n):
            print("{} / {}".format(i + 1, n))
            input_default(parameters[i])
        with open("setup.json", "w") as stream:
            json.dump(vars(self), stream, indent=2)
        print("setup updated")

    # generate http header from setup
    def headers(self) -> dict:
        headers = {"Accept": "application/json"}
        # if self.username:
        #     headers["User-Agent"] = self.username
        if self.email:
            headers["From"] = self.email
        return headers

    def load(self):
        try:
            with open("setup.json") as stream:
                data = json.load(stream)
        except FileNotFoundError:
            print("setup.json not found")
        except JSONDecodeError:
            print("setup.json is empty")
        for key, value in data.items():
            setattr(self, key, value)
        self.club = Club(self.club)


# this prints stuff in bold
def print_bold(s: str, end="\n", sep=" "):
    print("\033[1m" + s + "\033[0m", end=end, sep=sep)


# this inputs names separated by either white spaces or new lines
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


class Times:
    __dt = datetime.now(tz=timezone.utc)
    now = int(__dt.timestamp())

    # for potw
    this_week = __dt.replace(hour=9, minute=0, second=0, microsecond=0)
    __days = __dt.weekday()
    if __days < 3:
        __days = -(__days + 4)
    elif __days > 3:
        __days = __days - 3
    elif __dt < this_week:
        __days = -7
    else:
        __days = 0
    this_week += timedelta(days=__days)
    last_week = this_week - timedelta(days=7)
    next_week = this_week + timedelta(days=7)
    this_week = this_week.timestamp()
    last_week = last_week.timestamp()
    next_week = next_week.timestamp()

    # for loot.py
    months = []
    last90 = __dt - timedelta(days=90)
    while last90 <= __dt:
        months.append("{}/{:>02}".format(last90.year, last90.month))
        last90 = last90.replace(month=(last90.month + 1))
    months.reverse()
    last90 = int((__dt - timedelta(days=90)).timestamp())


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


# class FinishedGame:
#
#     def __init__(self, username: str, is_black: bool, result: str, end_time: int):
#         self.username = username
#         self.is_black = is_black
#         self.result = result
#         self.end_time = end_time


class ClubMatch:

    def __init__(self, match_id: str, status: str):
        self.match_id = match_id
        self.status = status
        if status not in ("registration", "in_progress", "finished"):
            raise ValueError("status must be 'registration', 'in_progress', or 'finished'")
        self.cheaters = []

    def add_cheater(self, username: str):
        self.cheaters.append(username)

    def __repr__(self):
        return self.match_id

    def __hash__(self):
        return hash(self.match_id)

    def __eq__(self, other):
        if not isinstance(other, ClubMatch):
            raise TypeError("comparing a ClubMatch instance with a non-ClubMatch instance")
        return self.match_id == other.match_id

    # def __lt__(self, other):
    #     if not isinstance(other, ClubMatch):
    #         raise TypeError("comparing a ClubMatch instance with a non-ClubMatch instance")
    #     return int(self.match_url) < int(other.match_url)

    # def __gt__(self, other):
    #     if not isinstance(other, ClubMatch):
    #         raise TypeError("comparing a ClubMatch instance with a non-ClubMatch instance")
    #     return int(self.match_url) > int(other.match_url)

    # def __le__(self, other):
    #     if not isinstance(other, ClubMatch):
    #         raise TypeError("comparing a ClubMatch instance with a non-ClubMatch instance")
    #     return int(self.match_url) <= int(other.match_url)

    # def __ge__(self, other):
    #     if not isinstance(other, ClubMatch):
    #         raise TypeError("comparing a ClubMatch instance with a non-ClubMatch instance")
    #     return int(self.match_url) >= int(other.match_url)


class Board:

    def __init__(
            self,
            match_id: str,
            board: str,
            username: str,
            white_result: str = "",
            black_result: str = "",
            white_endtime: int|None = None,
            black_endtime: int|None = None
    ):
        self.match_id = match_id
        self.board = board
        self.username = username
        self.white_result = white_result
        self.black_result = black_result
        self.white_endtime = white_endtime
        self.black_endtime = black_endtime


class Club:
    def __init__(self, name):
        self.name = name

    def get_members(self):
        return "https://api.chess.com/pub/club/{}/members".format(self.name)

    def get_matches(self):
        return "https://api.chess.com/pub/club/{}/matches".format(self.name)


def get_player_page(username: str):
    return "https://www.chess.com/member/{}".format(username)
