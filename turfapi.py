import requests
from datetime import datetime

from turfclasses import Coordinate, User, Region, Zone


class TurfAPI:
    BASE_URL = "https://api.turfgame.com/v4/"
    TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self):
        pass

    def fetch_zones_in_area(self, north_east: Coordinate, south_west: Coordinate):
        """Fetch zones in an area from the Turf API based on north-east and south-west coordinates"""
        url = f"{self.BASE_URL}zones"
        payload = [{
            "northEast": {"latitude": north_east.lat, "longitude": north_east.lon},
            "southWest": {"latitude": south_west.lat, "longitude": south_west.lon}
        }]

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return self._parse_zones(response.json())
        else:
            print(f"Error fetching zones: {response.status_code}")
            return []

    def _parse_zones(self, data):
        """Helper method to convert API data into Zone objects"""
        zones = []
        for item in data:
            zone = Zone(
                id=item['id'],
                name=item['name'],
                coordinate=Coordinate(item['latitude'], item['longitude']),
                takeover_points=item['takeoverPoints'],
                points_per_hour=item['pointsPerHour'],
                date_created=datetime.strptime(item['dateCreated'], self.TURF_TIME_FORMAT),
                current_owner=User(item['currentOwner']['id'], item['currentOwner']['name'])
            )
            zones.append(zone)
        return zones
