import argparse
import datetime
import json

from .announce import post_new_scores, post_leaderboard
from .aoc import get_leaderboard
from .webhook import get_message_builder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--newscores", default=False, dest="post_new_scores", action="store_true"
    )
    parser.add_argument(
        "--leaderboard", default=False, dest="post_leaderboard", action="store_true"
    )
    args = parser.parse_args()

    with open("config.json") as f:
        config = json.loads(f.read())
    session_key = config["session_key"]
    boards = config["boards"]
    for board in boards:
        leaderboard_id = board["id"]
        url = board["webhook"]
        message_builder = get_message_builder(url)
        year = datetime.datetime.now().year
        leaderboard = get_leaderboard(year, leaderboard_id, session_key)
        if args.post_new_scores:
            post_new_scores(leaderboard, message_builder, url)
        if args.post_leaderboard:
            post_leaderboard(leaderboard, message_builder, url)


if __name__ == "__main__":
    main()
