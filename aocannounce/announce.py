from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import json
import os
import pickle
import requests
from typing import Iterator, Tuple, TYPE_CHECKING


from .aoc import Leaderboard

if TYPE_CHECKING:  # Avoid circular import
    from .webhook import MessageBuilder


@dataclass
class Star:
    name: str
    day: int
    part: int
    time: datetime


def stars_since_prev(prev: datetime, leaderboard: Leaderboard) -> [Star]:
    new = []
    for _, m in leaderboard.members.items():
        if m.last_star() > prev:
            cdl = m.completion_day_level
            for day, parts in cdl.items():
                for part, timestamp in parts.items():
                    star_time = timestamp.as_datetime()
                    if star_time > prev:
                        new.append(Star(m.name, day, part, star_time))
    new.sort(key=lambda x: (x.time, x.part, x.day, x.name))
    return new


def total_stars(leaderboard: Leaderboard) -> Iterator[Tuple[str, int]]:
    members = sorted(
        leaderboard.members.values(),
        key=lambda m: (m.stars, m.local_score),
        reverse=True,
    )
    return ((m.name, m.stars) for m in members if m.stars > 0)


def send_message(msg, url):
    data = {"text": msg}
    requests.post(
        url, data=json.dumps(data), headers={"Content-Type": "application/json"}
    )


def post_new_scores(
    leaderboard: Leaderboard, message_builder: MessageBuilder, url: str
):
    filename = f"prev{leaderboard.owner_id}"
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            prev = pickle.load(f)
    else:
        prev = datetime.min
    stars = stars_since_prev(prev, leaderboard)
    if stars:
        message = message_builder.post_message(stars)
        send_message(message, url)
    with open(filename, "wb") as f:
        now = datetime.utcnow()
        pickle.dump(now, f)


def post_leaderboard(
    leaderboard: Leaderboard, message_builder: MessageBuilder, url: str
):
    results = total_stars(leaderboard)
    message = message_builder.post_leaderboard_message(results)
    send_message(message, url)
