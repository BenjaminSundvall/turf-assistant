from datetime import datetime
from bs4 import BeautifulSoup
import requests
import os
import numpy as np

TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
ZUNDIN_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_takeovers(zone_name, round_id):
    takeovers = []

    filename = 'zundin_data/zundin_' + zone_name + '_' + round_id + '.html'
    soup = None

    # If file exists, read from file, otherwise download file
    if os.path.exists(filename):
        # print('Reading from', filename)
        with open(filename, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
    else:
        url = 'https://frut.zundin.se/zone.php?zonename=' + zone_name + '&roundid=' + round_id
        # print('Downloading', filename, 'from', url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        with open(filename, 'w') as file:
            file.write(soup.prettify())

    # Find the table containing the zone takeovers
    table = soup.find(id='roundTakeovers').find('table')

    # Extract rows from the table body and add data to takeover list
    for tr in table.select('tr')[1:-1]:
        takeover = {}

        # Raw data
        takeover['who'] = tr.select('td')[0].text.strip()
        takeover['points'] = tr.select('td')[1].text.strip()
        takeover['duration'] = tr.select('td')[2].text.strip()
        takeover['datetime'] = tr.select('td')[3].select('script')[0].text.strip()[29:-4]
        dt = datetime.strptime(takeover['datetime'], ZUNDIN_TIME_FORMAT)
        # print('Datetime:', dt)

        # Derived data
        takeover['date'] = dt.day   # 1-31
        takeover['hour'] = dt.hour  # 0-23
        takeover['weekday'] = dt.isoweekday()   # 1-7 (Monday is 1)

        takeovers.append(takeover)

    return takeovers


def get_zone_data(zone_name, round_id):
    print('Getting data for', zone_name)
    takeovers = get_takeovers(zone_name, round_id)

    if not takeovers:
        return None

    zone_data = {
        'name': zone_name,
        'round_id': round_id,
        'takeovers': takeovers,
        'value': 0,
        'stdev_points': 0,
        'takes_hourly': [0] * 24,
        'zundin_url': 'https://frut.zundin.se/zone.php?zonename=' + zone_name + '&roundid=' + round_id
    }

    points = []

    for takeover in takeovers:
        # Ignore assists
        if not takeover['duration']:
            continue

        points.append(int(takeover['points']))
        zone_data['takes_hourly'][takeover['hour']] += 1

    # Calculate zone value
    zone_data['value'] = np.mean(points)
    zone_data['stdev_points'] = np.std(points)

    return zone_data


def download_zone_data(zone_name: str, round_id):
    takeovers = []

    filename = 'takeovers/' + zone_name + '_' + round_id + '.json'

    soup = None

    table = soup.find(id='roundTakeovers').find('table')
    for tr in table.select('tr')[1:-1]:
        takeover = {}

        # Raw data
        takeover['who'] = tr.select('td')[0].text.strip()
        takeover['points'] = tr.select('td')[1].text.strip()
        takeover['duration'] = tr.select('td')[2].text.strip()
        takeover['datetime'] = tr.select('td')[3].select('script')[0].text.strip()[29:-4]
        dt = datetime.strptime(takeover['datetime'], ZUNDIN_TIME_FORMAT)

        # Derived data
        takeover['date'] = dt.day   # 1-31
        takeover['hour'] = dt.hour  # 0-23
        takeover['weekday'] = dt.isoweekday()   # 1-7 (Monday is 1)

        takeovers.append(takeover)
    pass