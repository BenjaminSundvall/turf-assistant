import numpy as np
from zone import Coordinate
from datetime import datetime


TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
ZUNDIN_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def distance_m(coords1: Coordinate, coords2: Coordinate):
    """
    Calculate the distance between two coordinates in meters.
    """

    R = 6371000  # Earth radius in meters
    phi1 = np.radians(coords1.lat)
    phi2 = np.radians(coords2.lat)
    delta_phi = np.radians(coords2.lat - coords1.lat)
    delta_lambda = np.radians(coords2.lon - coords1.lon)

    a = np.sin(delta_phi / 2) * np.sin(delta_phi / 2) + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) * np.sin(delta_lambda / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def get_round_id(date: datetime):
    """
    Calculate the round id of a current date.
    """

    start_date = datetime(2010, 7, 10)
    months_since_start = 1 + (date.year - start_date.year) * 12 + date.month - start_date.month

    # Calculate datetime for round start this month (first sunday of he month at 12 pm)
    first_weekday_of_month = date.replace(day=1).weekday()
    round_start = date.replace(day=1 + (6 - first_weekday_of_month) % 7, hour=12, minute=0, second=0, microsecond=0)

    if date < round_start:
        months_since_start -= 1

    return months_since_start
