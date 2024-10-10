import requests
import json
from datetime import datetime, timezone


def get_request(url):
    response = requests.get(url)
    return response.json()


def post_request(url, data):
    response = requests.post(url, data)
    return response.json()


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def calculate_zone_values(zones):
    for zone in zones:
        date_created = datetime.strptime(zone['dateCreated'], '%Y-%m-%dT%H:%M:%S%z')
        time_since_creation = datetime.now(timezone.utc) - date_created
        zone['avgHold'] = time_since_creation / zone['totalTakeovers']
        zone['value'] = zone['takeoverPoints'] + zone['pointsPerHour'] * zone['avgHold'].total_seconds() / 3600

    zones.sort(key=lambda x: x['value'], reverse=True)
    return zones


def print_zone_info(zone):
    print('\n===================')
    print('Name:', zone['name'], '- ID:', zone['id'])
    print('Points:', zone['takeoverPoints'], '/', zone['pointsPerHour'])
    print('Avg hold duration:', zone['avgHold'])
    print('-------------------')
    print('Value:', zone['value'])
    print('===================')


# Print top 10 zones in Ryd, Linköping
ryd_request = json.dumps([{'northEast': {'latitude': 58.4204, 'longitude': 15.5783}, 'southWest': {'latitude': 58.4045, 'longitude': 15.5526}}])
zones = post_request('https://api.turfgame.com/v4/zones', data=ryd_request)
sorted_zones = calculate_zone_values(zones)

for zone in sorted_zones[:10]:
    print_zone_info(zone)


# ryd_request = json.dumps([{'northEast': {'latitude': 58.4204, 'longitude': 15.5783}, 'southWest': {'latitude': 58.4045, 'longitude': 15.5526}}])
# feed = get_request('https://api.turfgame.com/v4/zones')