"""Python wrapper for the Advent of Code leaderboard API"""
from datetime import datetime
from typing import Dict

from marshmallow_dataclass import dataclass
import requests


@dataclass
class Timestamp:
    get_star_ts: int

    def as_datetime(self) -> datetime:
        return datetime.utcfromtimestamp(self.get_star_ts)


@dataclass
class Member:
    id: int
    completion_day_level: Dict[int, Dict[int, Timestamp]]
    global_score: int
    name: str
    last_star_ts: int
    stars: int
    local_score: int

    def last_star(self) -> datetime:
        return datetime.utcfromtimestamp(self.last_star_ts)


@dataclass
class Leaderboard:
    owner_id: int
    members: Dict[int, Member]
    event: int


def get_leaderboard(year: int, leaderboard_id: int, session_key: str) -> Leaderboard:
    res = requests.get(
        f"https://adventofcode.com/{year}/leaderboard/private/"
        f"view/{leaderboard_id}.json",
        cookies={"session": session_key},
    ).json()
    return Leaderboard.Schema().load(res)
