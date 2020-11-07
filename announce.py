import argparse
import json
import os
import requests
import datetime
import time


def get_results(leaderboard_id, session_key):
    return requests.get(f'https://adventofcode.com/2019/leaderboard/private/view/{leaderboard_id}.json',
                        cookies={'session': session_key}).json()


def stars_since_prev(prev, res):
    new = []
    for _, m in res['members'].items():
        if int(m['last_star_ts']) > prev:
            cdl = m['completion_day_level']
            for day, parts in cdl.items():
                for part, inner in parts.items():
                    gst = int(inner['get_star_ts'])
                    if gst > prev:
                        new.append((m['name'], day, part, gst))
    new.sort(key=lambda x: (x[3], x[2], x[1], x[0]))
    return new


def total_stars(res):
    members = sorted(res['members'].values(), key=lambda m: (m['stars'], m['local_score']), reverse=True)
    return ((m['name'], m['stars']) for m in members if m['stars'] > 0)


def make_time_string(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S GMT')


def send_message(msg, url):
    data = {'text': msg}
    requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})


def post(stars, url):
    if 'hooks.slack.com' in url:
        sep = '\n'
    elif 'outlook.office.com' in url:
        sep = '<br />'
    else:
        raise RuntimeError(f'unable to determine webhook provider from url ({url})')
    s = sep.join(f'{star[0]} completed day {star[1]} part {star[2]} on {make_time_string(star[3])}' for star in stars)
    send_message(s, url)


def post_leaderboard(stars, url):
    if 'hooks.slack.com' in url:
        s = '*Stars* ⭐\n```' + '\n'.join(f'{s[1]:3d} {s[0]}' for s in stars) + '```'
    elif 'outlook.office.com' in url:
        # MS Teams doesn't handle line breaks in code pre-formatted blocks for whatever reason
        s = '**Stars** ⭐<br />' + '<br />'.join(f'{s[1]:3d} {s[0]}' for s in stars)
    else:
        raise RuntimeError(f'unable to determine webhook provider from url ({url})')
    send_message(s, url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--newscores', default=False, dest='post_new_scores', action='store_true')
    parser.add_argument('--leaderboard', default=False, dest='post_leaderboard', action='store_true')
    args = parser.parse_args()

    with open('config.json') as f:
        config = json.loads(f.read())
    session_key = config['session_key']
    boards = config['boards']
    for board in boards:
        leaderboard_id = board['id']
        url = board['webhook']
        res = get_results(leaderboard_id, session_key)
        if args.post_new_scores:
            filename = f'prev{leaderboard_id}'
            if os.path.exists(filename):
                with open(filename) as f:
                    prev = int(f.read())
            else:
                prev = 0
            stars = stars_since_prev(prev, res)
            if stars:
                post(stars, url)
            with open(filename, 'w') as f:
                f.write(str(int(time.time())))
        if args.post_leaderboard:
            leaderboard = total_stars(res)
            post_leaderboard(leaderboard, url)


if __name__ == '__main__':
    main()
