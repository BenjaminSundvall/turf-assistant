from datetime import datetime
from util import TURF_TIME_FORMAT


class Coordinate:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"({self.lat}, {self.lon})"

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    @staticmethod
    def from_json(json):
        return Coordinate(json['latitude'],
                          json['longitude'])

    def to_json(self):
        return {
            'latitude': self.lat,
            'longitude': self.lon
        }


class Zone:
    def __init__(self, id: int, name: str, coords: Coordinate, tp: int, pph: int, date_created: datetime, total_takeovers: int):
        self.id = id
        self.name = name
        self.coords = coords
        self.tp = tp    # Takeover Points
        self.pph = pph  # Points Per Hour
        self.date_created = date_created
        self.total_takeovers = total_takeovers

    def __str__(self):
        return f"{self.name} (ID: {self.id}))"

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def from_json(json: dict):
        return Zone(json['id'],
                    json['name'],
                    Coordinate(json['latitude'], json['longitude']),
                    json['takeoverPoints'],
                    json['pointsPerHour'],
                    datetime.strptime(json['dateCreated'], TURF_TIME_FORMAT),
                    json['totalTakeovers'])

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'longitude': self.coords.lon,
            'latitude': self.coords.lat,
            'takeoverPoints': self.tp,
            'pointsPerHour': self.pph,
            'dateCreated': self.date_created.strftime(TURF_TIME_FORMAT),
            'totalTakeovers': self.total_takeovers
        }


class Area:
    def __init__(self, northeast, southwest, zones, round_id):
        self.northeast = northeast
        self.southwest = southwest
        self.round_id = round_id
        self.zones = zones

    def __str__(self):
        return f"(NW: {self.northeast}, SE: {self.southwest})"

    def __eq__(self, other):
        return self.northeast == other.northeast and self.southwest == other.southwest and self.round_id == other.round_id

    @staticmethod
    def from_json(json: dict):
        return Area(Coordinate.from_json(json['northEast']),
                    Coordinate.from_json(json['southWest']),
                    json['zones'],
                    json['round_id'])

    def to_json(self):
        return {
            'northEast': self.northeast.to_json(),
            'southWest': self.southwest.to_json(),
            'zones': [zone.to_json() for zone in self.zones],
            'round_id': self.round_id
        }

