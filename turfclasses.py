from datetime import datetime
from util import sl_distance


class Coordinate:
    """ Coordinate class for representing a latitude and longitude pair """
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"({self.lat}, {self.lon})"

    def __add__(self, other):
        if not isinstance(other, Coordinate):
            raise ValueError("Only instances of Coordinate can be added together")
        return Coordinate(self.lat + other.lat, self.lon + other.lon)

    def __sub__(self, other):
        if not isinstance(other, Coordinate):
            raise ValueError("Only instances of Coordinate can be subtracted")
        return Coordinate(self.lat - other.lat, self.lon - other.lon)

    def __mul__(self, scalar):
        return Coordinate(self.lat * scalar, self.lon * scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Coordinate(self.lat / scalar, self.lon / scalar)

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    def to_list(self):
        return [self.lat, self.lon]


class User:
    """ User class for representing a Turf user """
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    def __eq__(self, other):
        return self.id == other.id


class Region:
    """ Region class for representing a Turf region """
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    def __eq__(self, other):
        return self.id == other.id


class Zone:
    """ Zone class for representing a Turf zone """
    def __init__(self, id: int, name: str, coordinate: Coordinate, takeover_points: int, points_per_hour: int, date_created: datetime, current_owner: User):
        self.id = id
        self.name = name
        self.coordinate = coordinate
        self.takeover_points = takeover_points
        self.points_per_hour = points_per_hour
        self.date_created = date_created
        self.current_owner = current_owner

    def __str__(self):
        return f"{self.name} (ID: {self.id}))"

    def __eq__(self, other):
        return self.id == other.id

    def distance_to(self, other_zone):
        return sl_distance(self.coordinate, other_zone.coordinate)


