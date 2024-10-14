from datetime import datetime
from util import Coordinate, TURF_TIME_FORMAT, sl_distance


class Zone:
    def __init__(self, id: int, name: str, coords: Coordinate, tp: int, pph: int, date_created: datetime, total_takeovers: int):
        self.id = id
        self.name = name
        self.coords = coords
        self.tp = tp    # Takeover Points
        self.pph = pph  # Points Per Hour
        self.date_created = date_created
        self.total_takeovers = total_takeovers

        self.value = 1

    def __str__(self):
        return f"{self.name} (ID: {self.id}))"

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def from_json(zone_json: dict):
        return Zone(zone_json['id'],
                    zone_json['name'],
                    Coordinate(zone_json['latitude'], zone_json['longitude']),
                    zone_json['takeoverPoints'],
                    zone_json['pointsPerHour'],
                    datetime.strptime(zone_json['dateCreated'], TURF_TIME_FORMAT),
                    zone_json['totalTakeovers'])

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

    @staticmethod
    def fetch_zones_in_area(self, ne: Coordinate, sw: Coordinate, round_id: int):
        pass

    def distance_to(self, other_zone):
        return sl_distance(self.coords, other_zone.coords)