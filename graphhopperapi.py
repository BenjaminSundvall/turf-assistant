import requests
from datetime import datetime
import polyline
import os

from turfclasses import Coordinate, User, Region, Zone
from apikeys import GRAPHHOPPER_API_KEY

import json
import folium

from util import load_from_json, save_to_json

class GraphHopperAPI:
    BASE_URL = "https://graphhopper.com/api/1/"
    TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self):
        pass

    def get_bike_route(self, start: Coordinate, finish: Coordinate):
        """Fetch zones in an area from the Turf API based on north-east and south-west coordinates"""
        filename = f'routes/{start.lat:.4f}_{start.lon:.4f}_to_{finish.lat:.4f}_{finish.lon:.4f}.json'

        # Check for cached data
        if os.path.exists(filename):
            print(f"{filename} already exists. Loading from file.")
            return load_from_json(filename)

        # If not cached, fetch from GraphHopper
        print(f"{filename} not found. Fetching from GraphHopper.")
        url = f"{self.BASE_URL}route?key=" + GRAPHHOPPER_API_KEY
        payload = {
            "points": [[start.lon, start.lat], [finish.lon, finish.lat]],   # NOTE: Inverted order of lat/lon
            "profile": "bike",
            "points_encoded": True
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            route = self._parse_route(response.json())
            save_to_json(route, filename)
            return route
        else:
            print(f"Error getting route: {response.status_code}")
            return {}


    def _parse_route(self, data):
        """Helper method to convert API data into Route object"""
        path = data['paths'][0]
        route = {}
        route['distance'] = path['distance']
        route['time'] = path['time']
        route['ascend'] = path['ascend']
        route['descend'] = path['descend']

        if path['points_encoded']:
            route['points'] = polyline.decode(path['points'], 5)
            route['snapped_waypoints'] = polyline.decode(path['snapped_waypoints'], 5)
        else:
            route['points'] = [[point[1], point[0]] for point in path['points']['coordinates']]
            route['snapped_waypoints'] = [[point[1], point[0]] for point in path['snapped_waypoints']['coordinates']]

        return route




# gh = GraphHopperAPI()
# start = Coordinate(58.4118, 15.5651)
# finish = Coordinate(58.3983, 15.5776)
# route = gh.get_bike_route(start, finish)


# # Draw map
# center = (start + finish) / 2
# m = folium.Map(location=(center.lat, center.lon), zoom_start=14)

# points = route['points']

# folium.PolyLine(points, color='red', weight=4).add_to(m)

# filename = 'routemap.html'
# print('Saving map to', filename)
# m.save(filename)