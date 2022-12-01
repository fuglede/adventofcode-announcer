"""Python wrapper for the Advent of Code leaderboard API"""
from datetime import datetime
from typing import Dict

from marshmallow_dataclass import dataclass
import requests


@dataclass
class Timestamp:
    get_star_ts: int
    star_index: int

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
    # We add a custom User-Agent to comply with
    # https://old.reddit.com/r/adventofcode/comments/z9dhtd/please_include_your_contact_info_in_the_useragent/
    res = requests.get(
        f"https://adventofcode.com/{year}/leaderboard/private/"
        f"view/{leaderboard_id}.json",
        cookies={"session": session_key},
        headers={"User-Agent": 'github.com/fuglede/adventofcode-announcer by github@fuglede.dk'}
    ).json()
    return Leaderboard.Schema().load(res)
