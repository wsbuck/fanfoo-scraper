import requests
import json
import base64
import time
import os
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

stat_categories = {
    'games_played': 0,
    'pass_attempts': 1,
    'pass_completions': 2,
    'pass_yards': 4,
    'pass_tds': 5,
    'pass_interceptions': 6,
    'sacks': 7,
    'rush_attempts': 8,
    'rush_yards': 9,
    'rush_tds': 10,
    'rec_targets': 78,
    'rec_receptions': 11,
    'rec_yards': 12,
    'rec_tds': 13,
}

season_codes = {
    '2015': '348',
    '2016': '359',
    '2017': '371',
    '2018': '380',
    '2019': '390',
}

REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


def get_stat(stat_list, stat_id):
    stat_id = str(stat_id)
    for stat in stat_list:
        data = stat['stat']
        if data['stat_id'] == stat_id:
            return float(data['value'])
    return 0.0


def get_access_token():
    authorization = base64.b64encode(
        CLIENT_ID.encode() + ':'.encode() + CLIENT_SECRET.encode()
    ).decode()

    headers = {
        'Authorization': f'Basic {authorization}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    url = 'https://api.login.yahoo.com/oauth2/get_token'
    payload = f'grant_type=refresh_token&redirect_uri= \
        https://twofiftysix.williambuck.dev&refresh_token={REFRESH_TOKEN}'
    
    resp = requests.request('POST', url=url, headers=headers, data=payload)

    if resp.status_code != 200:
        raise Exception('Could not retrieve Access Token')

    return resp.json()['access_token']


def main():

    qb = pd.read_csv('../data/QB_proj.csv')
    rb = pd.read_csv('../data/RB_proj.csv')
    te = pd.read_csv('../data/TE_proj.csv')
    wr = pd.read_csv('../data/WR_proj.csv')

    players = pd.concat([qb, rb, te, wr], sort=False)
    player_ids = players[players['data_src'] == 'Yahoo']['src_id']
    stats_df = pd.DataFrame(
        columns=[
            'player_id', 'season', 'week',
            'pass_attempts', 'pass_completions',
            'pass_yards', 'pass_tds', 'pass_interceptions', 'sacks',
            'rush_attempts', 'rush_yards', 'rec_targets', 'rec_receptions',
            'rec_yards', 'rec_tds',
        ]
    )

    url = 'https://fantasysports.yahooapis.com/fantasy/v2/player/{}/ \
        stats;type=week;week={}?format=json'

    for season in season_codes:
        access_token = get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        for i, player_id in enumerate(player_ids):
            time.sleep(30)
            print('\n******************\n')
            print("{} / {}".format(i + 1, len(player_ids)))
            print(player_id)
            for week in range(1, 15):
                season_code = season_codes[season]
                player_key = f'{season_code}.p.{player_id}'
                temp_url = url.format(player_key, week)
                resp = requests.request('GET', url=temp_url, headers=headers)
                if resp.status_code != 200:
                    break
                    print(f'Error retrieving player {player_key} for {week}')
                    # raise Exception('Error retrieving player data')
                stats = (
                    resp.json()['fantasy_content']
                    ['player'][1]['player_stats']['stats']
                )
                row = {}
                row['player_id'] = player_id
                row['season'] = season
                row['week']
                for stat_name in stat_categories:
                    row[stat_name] = get_stat(
                        stats, stat_categories[stat_name])
                stats_df = stats_df.append(row, ignore_index=True)
    
    stats_df.to_csv('./stats.csv')


if __name__ == '__main__':
    main()