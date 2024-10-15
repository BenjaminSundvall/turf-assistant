import requests
import json
import numpy as np
import os

import heapq

from old_zundin_scraper import get_zone_data
from gui import draw_map
from graph_old import Graph, ZoneEdge, ZoneNode, calculate_distance_meters

TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
GRAPH_CONNECTEDNESS = 3
POINT_FOCUS = 1


def add_area_stats(area):
    round_id = area['round_id']
    zone_values = []

    missing_zones = []

    for i, zone in enumerate(area['zones']):
        print(f"{i}/{len(area['zones'])} ({(100*i/len(area['zones'])):.1f}%) - {zone['name']}")

        zone['zone_data'] = get_zone_data(zone['name'], round_id)

        if not zone['zone_data']:
            print('Stats for zone', zone['name'], 'not available! (Zone might be too new)')
            missing_zones.append(zone)
            continue

        zone_value = zone['zone_data']['value']
        zone_values.append(zone_value)

        if zone_value > area['max_value']:
            area['max_value'] = zone_value
        if zone_value < area['min_value']:
            area['min_value'] = zone_value

    for zone in missing_zones:
        area['zones'].remove(zone)

    area['mean_value'] = np.mean(zone_values)
    area['stdev_value'] = np.std(zone_values)

    print('Number of zones:', len(area['zones']))
    print('Min value:', area['min_value'])
    print('Max value:', area['max_value'])
    print('Mean value:', area['mean_value'])
    print('Standard deviation:', area['stdev_value'])

    return area


def zones_in_area(northEast, southWest, round_id):
    filename = f'area_data/{round_id}_{northEast[0]:.6f}_{northEast[1]:.6f}_to_{southWest[0]:.6f}_{southWest[1]:.6f}.json'

    # If file exists, read from file, otherwise download file
    if os.path.exists(filename):
        print('Reading from', filename)
        with open(filename, 'r') as file:
            area = json.load(file)
            return area

    area = {
        'round_id': round_id,
        'northEast': northEast,
        'southWest': southWest,
        'zones': [],
        'min_value': 99999,
        'max_value': 0,
        'mean_value': 0,
        'stdev_value': 0,
    }
    url = 'https://api.turfgame.com/v4/zones'
    data = json.dumps([{'northEast': {'latitude': northEast[0], 'longitude': northEast[1]}, 'southWest': {'latitude': southWest[0], 'longitude': southWest[1]}}])
    area['zones'] = requests.post(url, data).json()
    area = add_area_stats(area)

    # Save area data to file
    with open(filename, 'w') as file:
        json.dump(area, file)

    return area



def simple_cost(distance, value):
    return distance / value


def create_area_graph(area):
    graph = Graph()

    # Add nodes
    for zone in area['zones']:
        graph.add_node(ZoneNode(zone))

    # Add edges
    for node in graph.get_nodes():
        for other_node in graph.get_nodes():
            # Ignore connection to self
            if node is other_node:
                continue

            # Filter out unreasonable connections to create a sparse graph
            sl_distance = calculate_distance_meters(node.coords, other_node.coords)
            if sl_distance < other_node.value * GRAPH_CONNECTEDNESS:
                # TODO: Add api call to graphhopper to calculate driving distance intead of straight line distance
                graph.add_edge(ZoneEdge(node, other_node, simple_cost))

    return graph


def generate_area(round_id, northEast, southWest):
    area = zones_in_area(northEast, southWest, round_id)
    graph = create_area_graph(area)

    return area, graph


if __name__ == '__main__':
    predefined_areas = {
        'ryd_full': {
            'northEast': [58.4217, 15.5888],
            'southWest': [58.4001, 15.5428],
            'start_zone': 'StudentRyd',
            'end_zone': 'VallaCircle'
        },
        'ryd_center': {
            'northEast': [58.4167, 15.5788],
            'southWest': [58.4051, 15.5528],
            'start_zone': 'StudentRyd',
            'end_zone': 'RydEast'
        },
        'tallboda': {
            'northEast': [58.4370, 15.7068],
            'southWest': [58.4114, 15.6335],
            'start_zone': 'Pinezone',
            'end_zone': 'Uppvinden'
        },
        'ryd_to_tallboda': {
            'northEast': [58.4370, 15.7068],
            'southWest': [58.4001, 15.5428],
            'start_zone': 'Kullen',
            'end_zone': 'DäBarrÅÅk'
        },
        'lkpg': {
            'northEast': [58.4541, 15.7265],
            'southWest': [58.3581, 15.4769],
            'start_zone': 'Kullen',
            'end_zone': 'DäBarrÅÅk'
        },
        'lkpg_plus': {
            'northEast': [58.5364, 15.7265],
            'southWest': [58.3581, 15.4769],
            'start_zone': 'Kullen',
            'end_zone': 'DäBarrÅÅk'
        },
        'boras': {
            'northEast': [57.8451, 13.0569],
            'southWest': [57.6818, 12.8690],
            'start_zone': 'BorStation',
            'end_zone': 'GötasMagasin'
        },
    }

    # Choose area and round
    area_name = 'ryd_full'
    round_id = '159'

    # Generate area data and graph
    area, graph = generate_area(round_id, predefined_areas[area_name]['northEast'], predefined_areas[area_name]['southWest'])

    # Do a graph search
    start_node = graph.get_node_by_name(predefined_areas[area_name]['start_zone'])
    end_node = graph.get_node_by_name(predefined_areas[area_name]['end_zone'])

    print('\nPerforming search from', start_node.name, 'to', end_node.name)
    cheapest_path = graph.cheapest_path(start_node, end_node)
    for i, node in enumerate(cheapest_path):
        print(f'{i}: {node.name} ({node.cost:.2f})')
    print('Total cost:', end_node.cost)

    expanded_path = graph.expanded_path(start_node, end_node, max_dist=1000)

    # Draw the map
    draw_map(area, graph, cheapest_path)