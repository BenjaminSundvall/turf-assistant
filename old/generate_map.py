from gui import FoliumGUI
import json
import os
import requests

from util import Coordinate, simple_cost
from turfclasses import Zone
from area import Area
from graph import Graph, build_graph, dijkstra_search
from old_zundin_scraper import get_zone_data

def load_area(ne: Coordinate, sw: Coordinate, round_id: id):
    filename = f'area_data/{round_id}_{ne.lon:.6f}_{ne.lat:.6f}_to_{sw.lon:.6f}_{sw.lat:.6f}.json'
    api_url = 'https://api.turfgame.com/v4/zones'

    # If file exists, read from file, otherwise download zones
    # if os.path.exists(filename):
    #     print('Reading from', filename)
    #     with open(filename, 'r') as file:
    #         area_json = json.load(file)
    #         return Area.from_json(area_json)

    # Get zones
    zones = []
    data = json.dumps([{'northEast': {'latitude': ne.lat, 'longitude': ne.lon}, 'southWest': {'latitude': sw.lat, 'longitude': sw.lon}}])
    response = requests.post(api_url, data).json()
    for zone_json in response:
        zone = Zone.from_json(zone_json)

        zone_data = get_zone_data(zone.name, round_id)
        if not zone_data:
            continue
        zone.value = zone_data['value']

        zones.append(zone)

    # Create area
    area = Area(ne, sw, zones, round_id)

    # Save area data to file
    with open(filename, 'w') as file:
        json.dump(area.to_json(), file)

    return area





if __name__ == '__main__':
    predefined_areas = {
        'ryd_full': {
            'northEast': {'latitude': 58.4217, 'longitude': 15.5888},
            'southWest': {'latitude': 58.4001, 'longitude': 15.5428},
            'start_zone': 'StudentRyd',
            'end_zone': 'VallaCircle'
        },
        'ryd_center': {
            'northEast': {'latitude': 58.4167, 'longitude': 15.5788},
            'southWest': {'latitude': 58.4051, 'longitude': 15.5528},
            'start_zone': 'StudentRyd',
            'end_zone': 'RydEast'
        },
        'tallboda': {
            'northEast': {'latitude': 58.4370, 'longitude': 15.7068},
            'southWest': {'latitude': 58.4114, 'longitude': 15.6335},
            'start_zone': 'Pinezone',
            'end_zone': 'Uppvinden'
        },
        'ryd_to_tallboda': {
            'northEast': {'latitude': 58.4370, 'longitude': 15.7068},
            'southWest': {'latitude': 58.4001, 'longitude': 15.5428},
            'start_zone': 'Kullen',
            'end_zone': 'DäBarrÅÅk'
        },
        'lkpg': {
            'northEast': {'latitude': 58.4541, 'longitude': 15.7265},
            'southWest': {'latitude': 58.3581, 'longitude': 15.4769},
            'start_zone': 'Kullen',
            'end_zone': 'DäBarrÅÅk'
        },
        'lkpg_plus': {
            'northEast': {'latitude': 58.5364, 'longitude': 15.7265},
            'southWest': {'latitude': 58.3581, 'longitude': 15.4769},
            'start_zone': 'Kullen',
            'end_zone': 'DäBarrÅÅk'
        },
        'borås': {
            'northEast': {'latitude': 57.8451, 'longitude': 13.0569},
            'southWest': {'latitude': 57.6818, 'longitude': 12.8690},
            'start_zone': 'BorStation',
            'end_zone': 'GötasMagasin'
        },
    }

    # Choose area and round
    area_name = 'ryd_full'
    round_id = '159'

    # Generate area data
    area = load_area(Coordinate.from_json(predefined_areas[area_name]['northEast']),
                     Coordinate.from_json(predefined_areas[area_name]['southWest']),
                     round_id)

    # Create GUI
    center = (area.northeast + area.southwest) / 2
    gui = FoliumGUI(center)

    # Draw bounding box
    bbox_text = f"""
                <div style="background-color: white; padding: 10px; border: 1px solid black;">
                    <p>{len(area.zones)} zones</p>
                    <p>Round {round_id}</p>
                </div>
                """
    gui.draw_bbox(area.northeast, area.southwest, bbox_text)

    # Draw zones
    gui.draw_zones(area.zones)

    # Draw graph
    graph = build_graph(area, simple_cost)
    gui.draw_graph(graph)

    # Draw path
    start_node = graph.get_node_by_name(predefined_areas[area_name]['start_zone'])
    end_node = graph.get_node_by_name(predefined_areas[area_name]['end_zone'])
    path = dijkstra_search(graph, start_node, end_node)

    # Save map
    filename = 'maps/map_' + round_id + '.html'
    gui.save_map(filename)




    # draw_map(area, graph, cheapest_path)

    # area, graph = generate_area(round_id, predefined_areas[area_name]['northEast'], predefined_areas[area_name]['southWest'])

    # # Do a graph search
    # start_node = graph.get_node_by_name(predefined_areas[area_name]['start_zone'])
    # end_node = graph.get_node_by_name(predefined_areas[area_name]['end_zone'])

    # print('\nPerforming search from', start_node.name, 'to', end_node.name)
    # cheapest_path = graph.cheapest_path(start_node, end_node)
    # for i, node in enumerate(cheapest_path):
    #     print(f'{i}: {node.name} ({node.cost:.2f})')
    # print('Total cost:', end_node.cost)

    # expanded_path = graph.expanded_path(start_node, end_node, max_dist=1000)