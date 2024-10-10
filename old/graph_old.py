import heapq
import numpy as np

GRAPH_CONNECTEDNESS = 3
POINT_FOCUS = 1

def calculate_distance_meters(coords1, coords2):
    lat1, lon1 = coords1
    lat2, lon2 = coords2

    R = 6371000  # Earth radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2) * np.sin(delta_phi / 2) + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) * np.sin(delta_lambda / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


class ZoneEdge:
    def __init__(self, start, finish, cost_fn):
        self.start = start
        self.finish = finish
        self.distance = calculate_distance_meters(start.coords, finish.coords)
        self.finish_value = finish.value
        self.cost = cost_fn(self.distance, self.finish_value)
        self.visited = False

    def reset_data(self):
        self.visited = False


class ZoneNode:
    def __init__(self, zone):
        self.zone = zone
        self.name = zone['name']
        self.coords = [zone['latitude'], zone['longitude']]
        self.value = zone['zone_data']['value']
        self.reset_data()

    def reset_data(self):
        self.cost = 0
        self.visited = False
        self.prev_node = None
        self.prev_edge = None


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def reset_data(self):
        for node in self.nodes:
            node.reset_data()
        for edge in self.edges:
            edge.reset_data()

    def add_node(self, node):
        self.nodes.append(node)

    def get_nodes(self):
        return self.nodes

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_edges(self):
        return self.edges

    def get_node_by_name(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_neighboring_nodes(self, node):
        neighbors = []
        for edge in self.edges:
            if edge.start == node:
                neighbors.append(edge.finish)
        return neighbors

    # TODO: Change to A* search by adding heuristic
    def cheapest_path(self, start_node, end_node):
        """Find the shortest path between two nodes using Dijkstra's algorithm."""
        self.reset_data()

        # Initialize distances and priority queue
        for node in self.get_nodes():
            node.cost = float('inf')
        start_node.cost = 0
        priority_queue = [(0, start_node)]
        start_node.visited = True

        while priority_queue:
            current_cost, current_node = heapq.heappop(priority_queue)

            # If we reached the end node, reconstruct the path
            if current_node == end_node:
                nodes = []

                while current_node:
                    nodes.append(current_node)
                    current_node = current_node.prev_node
                return nodes[::-1]

            # Explore neighbors
            for edge in self.get_edges():
                if edge.start == current_node:
                    neighbor_node = edge.finish
                # elif edge.finish == current_node:
                #     neighbor = edge.start
                else:
                    continue

                new_cost = current_node.cost + edge.cost

                # If a shorter path to the neighbor is found
                if new_cost < neighbor_node.cost:
                    neighbor_node.cost = new_cost
                    neighbor_node.prev_node = current_node
                    neighbor_node.prev_edge = edge
                    heapq.heappush(priority_queue, (new_cost, neighbor_node))
                    if not neighbor_node.visited:
                        neighbor_node.visited = True

        return None


    def expanded_path(self, start_node, end_node, max_dist):
        path = self.cheapest_path(start_node, end_node)

        total_dist = 0
        for dist in [node.prev_edge.distance for node in path if node.prev_edge]:
            total_dist += dist

        total_cost = 0
        for cost in [node.prev_edge.cost for node in path if node.prev_edge]:
            total_cost += cost

        print(f"Calculating expanded path from {start_node.name} to {end_node.name} with max distance {max_dist} meters")
        print(f"Shortest path distance: {total_dist}")
        print(f"Shortest path cost: {total_cost}")

        while total_dist < max_dist:
            cheapest_node = None
            cheapest_dist = float('inf')
            for path_node in path:
                prev_node = path_node.prev_node
                for other_node in self.get_nodes():
                    if other_node in path:
                        continue

                    # dist_diff =

                    dist = calculate_distance_meters(path_node.coords, other_node.coords)
                    if dist < max_dist - total_dist:
                        path = self.cheapest_path(path_node, other_node)
                        total_dist += dist
                        break
                prev_node = path_node.prev_node

