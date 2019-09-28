import requests
import json
import pandas as pd

from bs4 import BeautifulSoup
from requests.models import PreparedRequest

def name_cleanup(name):
    name = name.lower()
    name = name.replace('notes', '').replace('note', '')
    name = name.replace('no', '')
    name = name.replace('player', '').replace('players', '')
    name = name.replace('\n', '').replace('jr.', '').replace('sr.', '')
    name = name.replace('iii', '').replace('new', '')
    name = name.strip()
    name = name.split()
    return name[0] + ' ' + name[1]


def scrapeYahoo(season, week, position):
    url = 'https://football.fantasysports.yahoo.com/f1/47241/players'
    drop_cols = [
        0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 17, 19, 20, 24,
        25, 30, 31, 32, 33, 34, 35, 36, 37
    ]
    col_names = [
        'name', 'pass_att', 'pass_comp', 'pass_yds', 'pass_td', 'pass_int',
        'pass_sack', 'rush_att', 'rush_yds', 'rush_td', 'rec_tgt', 'rec_rec',
        'rec_yds', 'rec_td'
    ]
    all_players = pd.DataFrame(columns=col_names)

    for count in range(0, 300, 25):
        querystring = {
            'sort': 'PTS',
            'sdir': '1',
            'status': 'A',
            'pos': '{}'.format(position),
            'stat1': 'S_PW_{}'.format(week),
            'jsenabled': '0',
            'count': '{}'.format(count)
        }
        req = PreparedRequest()
        req.prepare_url(url, querystring)
        tables = pd.read_html(req.url)
        players = tables[1]
        players.drop(players.columns[drop_cols], axis=1, inplace=True)
        players.columns = col_names
        players['name'] = players['name'].apply(name_cleanup)
        if len(players) == 0:
            break
        all_players = all_players.append(players, ignore_index=True)
    
    return all_players


def scrapeNFL(season, week, position):
    url = "https://api.fantasy.nfl.com/v1/players/stats"
    querystring = {
        "statType": "weekProjectedStats",
        "week": "{}".format(week),
        "season": "{}".format(season),
        "position": "{}".format(position),
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
    # print(scrapeNFL(2019, 0).head())
    print(scrapeYahoo('2019', '4', 'QB'))


if __name__ == "__main__":
    main()
