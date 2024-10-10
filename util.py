import numpy as np
from zone import Coordinate


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
