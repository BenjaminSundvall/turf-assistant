from datetime import datetime
from dateutil.relativedelta import relativedelta

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

    def as_list(self):
        return [self.lat, self.lon]


class Round:
    """ Round class for representing a Turf round """

    FIRST_ROUND_START = datetime(2010, 7, 10, 12, 0, 0)

    def __init__(self, round_id: int):
        self.round_id = round_id

        # Calculate start and end dates
        self.start_date = Round.get_round_start(round_id)
        self.end_date = Round.get_round_start(round_id + 1) - relativedelta(seconds=1)

    def __str__(self):
        return f"Round {self.round_id} ({self.start_date} - {self.end_date})"

    def __eq__(self, other):
        return self.round_id == other.id

    @staticmethod
    def get_round_start(round_id: int):
        """ Calculate the start date of a month """
        first_day_of_month = Round.FIRST_ROUND_START.replace(day=1) + relativedelta(months=round_id - 1)
        days_until_sunday = (6 - first_day_of_month.weekday()) % 7
        round_start_date = first_day_of_month + relativedelta(days=days_until_sunday)
        return round_start_date

    @staticmethod
    def get_round_from_date(date: datetime):
        """ Calculate the round id of a current date. """

        months_since_start = 1 + 12*(date.year - Round.FIRST_ROUND_START.year) + (date.month - Round.FIRST_ROUND_START.month)

        # Calculate datetime for round start this month (first sunday of he month at 12 pm)
        first_day_of_month = date.replace(day=1)
        days_until_sunday = (6 - first_day_of_month.weekday()) % 7
        round_start_date = first_day_of_month + relativedelta(days=days_until_sunday)

        if date < round_start_date:
            months_since_start -= 1

        return months_since_start



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

        # Needs to be added manually later
        self.stats = None

    def __str__(self):
        return f"{self.name} (ID: {self.id}))"

    def __eq__(self, other):
        return self.id == other.id

    # TODO: Move this somewhere else or delete?
    def distance_to(self, other_zone):
        return sl_distance(self.coordinate, other_zone.coordinate)

    def value(self, date: datetime):
        """Calculate the value of the zone at a specific time"""
        if not self.stats:
            raise ValueError("Zone stats not set")

        estimated_hold_hrs = self.stats.estimate_hold_time(date, method='mean') / 3600
        return self.takeover_points + self.points_per_hour * estimated_hold_hrs

