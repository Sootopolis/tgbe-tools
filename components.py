import json
from datetime import timedelta
from json import JSONDecodeError


class Player:

    def __init__(
            self,
            username: str,
            player_id: int | str = 0
    ):
        self.username = username
        self.player_id = player_id

    def get_profile(self):
        return "https://api.chess.com/pub/player/{}".format(self.username)

    def get_homepage(self):
        return "https://www.chess.com/member/{}".format(self.username)

    def get_clubs(self):
        return "https://api.chess.com/pub/player/{}/clubs".format(self.username)

    def get_stats(self):
        return "https://api.chess.com/pub/player/{}/stats".format(self.username)

    def get_games(self):
        return "https://api.chess.com/pub/player/{}/games".format(self.username)

    def get_archive(self, month: str):
        return "https://api.chess.com/pub/player/{}/games/{}".format(self.username, month)

    def __repr__(self):
        return self.username

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        return self.username == other.username

    def __lt__(self, other):
        return self.username < other.username

    def __gt__(self, other):
        return self.username > other.username

    def __le__(self, other):
        return self.username <= other.username

    def __ge__(self, other):
        return self.username >= other.username


class Member(Player):

    def __init__(
            self,
            username: str,
            player_id: int | str = 0,
            timestamp: int | str = 0,
            is_closed: bool | str = False,
            is_former: bool | str = False
    ):
        super().__init__(username=username, player_id=player_id)
        self.timestamp = int(timestamp)
        self.is_closed = bool(int(is_closed))
        self.is_former = bool(int(is_former))
        # self.__W = 0
        # self.__D = 0
        # self.__L = 0
        # self.__last_activity = 0
        # self.__last_point = 0

    def to_csv_row(self):
        return [
            self.username,
            str(self.player_id),
            str(self.timestamp),
            str(int(self.is_closed)),
            str(int(self.is_former))
        ]

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

    # two Member objects are considered equal if they share the same username,
    # player_id (if both are specified), and timestamp (if both are specified)
    def __eq__(self, other):
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
                hasattr(other, "timestamp") and
                other.timestamp and
                self.timestamp != other.timestamp
        ):
            return False
        return True

    def __hash__(self):
        return hash(self.username)


class Candidate(Player):

    def __init__(
            self,
            username: str,
            player_id: int | str = 0,
            expiry: int | str = 0,
            invited: bool | str = False,
            joined: bool | str = False
    ):
        super().__init__(username=username, player_id=player_id)
        self.expiry = int(expiry)
        self.invited = bool(int(invited))
        self.joined = bool(int(joined))

    def to_csv_row(self):
        return [
            self.username,
            str(self.player_id),
            str(self.expiry),
            str(int(self.invited)),
            str(int(self.joined))
        ]


class ClubMatch:

    def __init__(
            self,
            match_id: str,
            status: str,
            boards: int | str,
            end_time: int | str = 0,
            cheaters: list[str] | str = ""
    ):
        self.match_id = match_id
        self.status = status
        self.boards = int(boards)
        self.end_time = int(end_time)
        if isinstance(cheaters, str):
            self.cheaters = cheaters.split()
        else:
            self.cheaters = cheaters

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


class Game:

    def __init__(self, result: str = "", end_time: int = 0):
        self.result = result
        self.end_time = end_time

    def __bool__(self):
        return bool(self.result)

    def finish(self, result: str, end_time: int):
        self.result = result
        self.end_time = end_time


class Board:

    def __init__(
            self,
            club_match: ClubMatch,
            board: str,
            member: Member,
            opponent: str,
            white: Game = Game(),
            black: Game = Game(),
            we_cheated: bool = False,
            op_cheated: bool = False
    ):
        self.club_match = club_match
        self.board = board
        self.member = member
        self.opponent = opponent
        self.white = white
        self.black = black
        self.we_cheated = we_cheated
        self.op_cheated = op_cheated

    def finish(self, is_white: bool, result: str, end_time: int):
        if is_white:
            self.white.finish(result, end_time)
        else:
            self.black.finish(result, end_time)

    def __repr__(self):
        return self.club_match.match_id + "/" + self.board

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if not isinstance(other, Board):
            raise TypeError("comparing a Board instance with a non-Board instance")
        return repr(self) == repr(other)


class Club:
    def __init__(self, name):
        self.name = name

    def get_members(self):
        return "https://api.chess.com/pub/club/{}/members".format(self.name)

    def get_matches(self):
        return "https://api.chess.com/pub/club/{}/matches".format(self.name)

    def get_profile(self):
        return "https://api.chess.com/pub/club/{}".format(self.name)

    def __repr__(self):
        return self.name


class Setup:

    def __init__(self):
        self.club = ""
        self.email = ""
        self.username = ""
        self.avoid_admins = 1
        self.allow_re_invitations = 1
        self.clear_uninvitable_cache = 1
        self.invited_expiry = 180
        self.scanned_expiry = 30
        self.timeout_expiry = 90
        self.max_clubs = 30
        self.max_move_time = 18
        self.max_offline = 48
        self.min_cm = 12
        self.min_cm_ongoing = 2
        self.max_ongoing = 100
        self.min_elo = 1000
        self.max_elo = 2300
        self.min_score_rate = 0.45
        self.max_score_rate = 0.85

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
        self.invited_expiry = int(timedelta(days=self.invited_expiry).total_seconds())
        self.scanned_expiry = int(timedelta(days=self.scanned_expiry).total_seconds())
        self.timeout_expiry = int(timedelta(days=self.timeout_expiry).total_seconds())
        self.max_offline = int(timedelta(hours=self.max_offline).total_seconds())
        self.max_move_time = int(timedelta(hours=self.max_move_time).total_seconds())


# this prints stuff in bold
def print_bold(s: str, end="\n", sep=" "):
    print("\033[1m" + s + "\033[0m", end=end, sep=sep)


def get_player_profile(username: str):
    return "https://www.chess.com/member/{}".format(username)


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
