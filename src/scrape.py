import requests
import json
import pandas as pd

from bs4 import BeautifulSoup


def scrapeNFL(season, week):
    url = "https://api.fantasy.nfl.com/v1/players/stats"
    querystring = {
        "statType": "seasonProjectedStats",
        "week": "{}".format(week),
        "season": "{}".format(season),
        "format": "json"
    }
    headers = {
        "cache-control": "no-cache",
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception('Error requesting data')

    data = json.loads(response.text)
    players = data['players']
    cols = [
        'id', 'name', 'position', 'def_td', 'def_sack',
        'def_safety', 'def_int', 'def_fum_rec', 'def_blk',
        'def_pts_g', 'rush_yds', 'rush_td', 'rec_rec', 'rec_yds',
        'rec_td', 'pass_yds', 'pass_td', 'pass_int'
    ]
    season_projections = pd.DataFrame(columns=cols)

    for player in players:
        stats = player.get('stats')
        projections = {
            'id': player.get('id'),
            'name': player.get('name'),
            'position': player.get('position'),
            'def_td': stats.get('50', 0),
            'def_sack': stats.get('45', 0),
            'def_safety': stats.get('49', 0),
            'def_int': stats.get('46', 0),
            'def_fum_rec': stats.get('47', 0),
            'def_blk': stats.get('51', 0),
            'def_pts_g': stats.get('54', 0),
            'rush_yds': stats.get('14', 0),
            'rush_td': stats.get('15', 0),
            'rec_rec': stats.get('20', 0),
            'rec_yds': stats.get('21', 0),
            'rec_td': stats.get('22', 0),
            'pass_yds': stats.get('5', 0),
            'pass_td': stats.get('6', 0),
            'pass_int': stats.get('7', 0)
        }
        season_projections = season_projections.append(
            projections, ignore_index=True)
    return season_projections


def main():
    print(scrapeNFL(2019, 0).head())


if __name__ == "__main__":
    main()