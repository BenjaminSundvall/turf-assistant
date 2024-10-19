from datetime import datetime
from typing import List

from graphhopperapi import GraphHopperAPI
from turfclasses import Zone
from util import sl_distance


class Edge:
    def __init__(self, start, finish, cost: float, route=None):
        self.start = start
        self.finish = finish
        self.cost = cost
        self.route = route


class Node:
    def __init__(self, zone: Zone):
        self.zone = zone
        self.edges = []

        # For search algorithms
        self.cost = 0
        self.visited = False
        self.previous = None
        self.next = None

    def add_edge(self, edge: Edge):
        assert type(edge) == Edge, f"{edge} ({type(edge)}) is not of type Edge!"
        self.edges.append(edge)

    def remove_edge(self, edge: Edge):
        self.edges.remove(edge)

    def __str__(self):
        return f"Node: {self.zone.name}"


class Graph:
    def __init__(self, graph_connectedness: float=4):
        self.graph_connectedness = graph_connectedness
        self.nodes = []

    def add_node(self, node: Node):
        assert type(node) == Node, f"{node} ({type(node)}) is not of type Node!"
        self.nodes.append(node)

    def get_node_by_name(self, name: str):
        for node in self.nodes:
            if node.zone.name == name:
                return node
        return None


def build_graph(zones: List[Zone], date: datetime):
    graph = Graph()
    gh_api = GraphHopperAPI()

    for zone in zones:
        node = Node(zone)
        graph.add_node(node)

    for node in graph.nodes:
        # print('Adding edges for', node.zone.name)
        for other_node in graph.nodes:
            if node is other_node:
                continue

            # Filter out unreasonable connections to create a sparse graph
            if sl_distance(node.zone.coordinate, other_node.zone.coordinate) > graph.graph_connectedness * other_node.zone.value(date): # dist / value > graph_connectedness
                continue

            bike_route = gh_api.get_bike_route(node.zone.coordinate, other_node.zone.coordinate)
            edge_cost = bike_route['distance'] / other_node.zone.value(date)

            edge = Edge(node, other_node, edge_cost, bike_route)
            node.add_edge(edge)

    return graph


def dijkstra_search(graph: Graph, start: Node, finish: Node):
    print('Performing search from', start.zone.name, 'to', finish.zone.name)

    for node in graph.nodes:
        node.visited = False
        node.cost = float('inf')
        node.previous = None

    start.cost = 0
    current = start

    while current != finish:
        # print(current.zone.name)
        for edge in current.edges:
            if edge.finish.cost > current.cost + edge.cost:
                edge.finish.cost = current.cost + edge.cost
                edge.finish.previous = current

        current.visited = True

        min_cost = float('inf')
        for node in graph.nodes:
            if not node.visited and node.cost < min_cost:
                min_cost = node.cost
                current = node

    path = []
    while current is not None:
        path.append(current)
        prev = current.previous
        if prev:
            prev.next = current
        current = prev

    return path[::-1]


