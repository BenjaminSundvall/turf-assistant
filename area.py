from typing import List

from turfclasses import Coordinate, Zone

class Area:
    def __init__(self, northeast: Coordinate, southwest: Coordinate, zones: List[Zone], round_id: int):
        self.northeast = northeast
        self.southwest = southwest
        self.round_id = round_id
        self.zones = zones

        self.mean_value = 0
        self.stdev_value = 0

    def __str__(self):
        return f"(NW: {self.northeast}, SE: {self.southwest})"

    def __eq__(self, other):
        return self.northeast == other.northeast and self.southwest == other.southwest and self.round_id == other.round_id


    @staticmethod
    def from_json(area_json: dict):
        return Area(Coordinate.from_json(area_json['northEast']),
                    Coordinate.from_json(area_json['southWest']),
                    [Zone.from_json(zone_json) for zone_json in area_json['zones']],
                    area_json['round_id'])


    def to_json(self):
        return {
            'northEast': self.northeast.to_json(),
            'southWest': self.southwest.to_json(),
            'zones': [zone.to_json() for zone in self.zones],
            'round_id': self.round_id
        }


    def fetch_zones(self):
        pass
