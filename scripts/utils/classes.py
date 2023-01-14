from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple
from singleton_decorator import singleton


@singleton
@dataclass(frozen=True)
class Config:

    club_name: str = ""
    email: str = ""
    username: str = ""
    avoid_admins: bool = True
    allow_repeat: bool = True
    max_clubs: int = 32
    min_matches_played: int = 12
    min_matches_ongoing: int = 1
    max_games_ongoing: int = 100
    min_elo: int = 1000
    max_elo: int = 2300
    min_score_rate: float = 0.45
    max_score_rate: float = 0.90
    invited_expiry: int = 180
    timeout_expiry: int = 90
    scanned_expiry: int = 30
    max_offline: int = 48
    max_move_time: int = 18

    def get_request_headers(self):
        headers = {"Accept": "application/json"}
        if self.email:
            headers["From"] = self.email
        return headers


@dataclass
class Player:

    username: str = ""
    player_id: int = 0

    def get_homepage(self):
        return f"https://www.chess.com/member/{self.username}"

    def get_profile(self):
        return f"https://api.chess.com/pub/player/{self.username}"

    def get_clubs(self):
        return f"https://api.chess.com/pub/player/{self.username}/clubs"

    def get_stats(self):
        return f"https://api.chess.com/pub/player/{self.username}/stats"

    def get_games(self):
        return f"https://api.chess.com/pub/player/{self.username}/games"

    def get_archive(self, yyyymm: str):
        return (
            f"https://api.chess.com/pub/player/{self.username}/games/{yyyymm}"
        )

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


@dataclass
class Member(Player):

    join_time: int = 0
    is_closed: bool = False
    is_former: bool = False
    wins: int = 0
    losses: int = 0
    draws: int = 0
    points: float = field(init=False)

    def __post_init__(self):
        self.points = self.wins + self.draws / 2

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        if self.username != other.username:
            return False
        if (
            self.player_id
            and other.player_id
            and self.player_id != other.player_id
        ):
            return False
        if (
            isinstance(other, Member)
            and self.join_time
            and other.join_time
            and self.join_time != other.join_time
        ):
            return False
        return True


@dataclass
class Candidate(Player):

    expiry: int = 0
    is_invited: bool = False
    has_joined: bool = False


@dataclass
class Club:

    name: str = ""

    def get_members(self):
        return f"https://api.chess.com/pub/club/{self.name}/members"

    def get_matches(self):
        return f"https://api.chess.com/pub/club/{self.name}/matches"

    def get_profile(self):
        return f"https://api.chess.com/pub/club/{self.name}"


@dataclass
class Result:
    @property
    def win(self):
        return 1.0

    @property
    def draw(self):
        return 0.5

    @property
    def loss(self):
        return 0.0


class ResultInfo(NamedTuple):
    code: str
    category: str


class GameResult(Enum):

    win = "win"
    checkmate = "checkmated"
    agreement = "agreed"
    repetition = "repetition"
    timeout = "timeout"
    resignation = "resigned"
    stalemate = "stalemate"
    loss = "lose"
    insufficient_material = "insufficient"
    fifty = "50move"
    abandonment = "abandoned"
    timevsinsufficient = "timevsinsufficient"
