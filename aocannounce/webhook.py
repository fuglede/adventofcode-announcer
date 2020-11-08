from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterator, Tuple

from .announce import Star


class MessageBuilder(ABC):
    @staticmethod
    def _post_message_parts(stars: [Star]) -> Iterator[str]:
        return (
            f"{'⭐' if star.part == 1 else '🌟'} {star.name} completed "
            f"day {star.day} part {star.part} on {star.time}"
            for star in stars
        )

    @abstractmethod
    def post_message(self, stars: [Star]) -> str:
        pass

    @staticmethod
    def _post_leaderboard_message_parts(
        results: Iterator[Tuple[str, int]]
    ) -> Iterator[str]:
        return (f"{s[1]:3d} {s[0]}" for s in results)

    @abstractmethod
    def post_leaderboard_message(self, results: Iterator[Tuple[str, int]]) -> str:
        pass


class TeamsMessageBuilder(MessageBuilder):
    def post_message(self, stars: [Star]) -> str:
        return "<br />".join(self._post_message_parts(stars))

    def post_leaderboard_message(self, results: Iterator[Tuple[str, int]]) -> str:
        # MS Teams is unable to handle line breaks in code pre-formatted blocks for
        # whatever reason.
        return "**Stars** ⭐<br />" + "<br />".join(
            self._post_leaderboard_message_parts(results)
        )


class SlackMessageBuilder(MessageBuilder):
    def post_message(self, stars: [Star]) -> str:
        return "\n".join(self._post_message_parts(stars))

    def post_leaderboard_message(self, results: Iterator[Tuple[str, int]]) -> str:
        return (
            "*Stars* ⭐\n```"
            + "\n".join(self._post_leaderboard_message_parts(results))
            + "```"
        )


def get_message_builder(url: str) -> MessageBuilder:
    if "hooks.slack.com" in url:
        return SlackMessageBuilder()
    if "outlook.office.com" in url:
        return TeamsMessageBuilder()
    raise RuntimeError(f"unable to determine webhook provider from url ({url})")
