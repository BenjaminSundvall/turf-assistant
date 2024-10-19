from datetime import datetime
import folium
import folium.plugins as plugins
from typing import List

from turfclasses import Zone
from area import Area
from graph import Graph


class GUI:
    def __init__(self, center):
        self.center = center

    def draw_bbox(self, ne, sw, info_text):
        raise NotImplementedError("Not implemented, call a subclass!")

    def draw_zones(self, zones):
        raise NotImplementedError("Not implemented, call a subclass!")

    def draw_graph(self, graph):
        raise NotImplementedError("Not implemented, call a subclass!")

    def save_map(self, filename):
        raise NotImplementedError("Not implemented, call a subclass!")


class FoliumGUI(GUI):
    def __init__(self, center, zoom_start=14):
        super().__init__(center)
        self.map = folium.Map(location=(center.lat, center.lon), zoom_start=zoom_start)


    def draw_bbox(self, ne, sw):
        bbox_group = folium.FeatureGroup(name='Bounding Box', show=True).add_to(self.map)

        # Draw bounding box
        folium.Rectangle(
            bounds=[(sw.lat, sw.lon), (ne.lat, ne.lon)],
            color='blue',
            fill=False,
        ).add_to(bbox_group)


    def draw_zones(self, zones, date=datetime.now()):
        marker_group = folium.FeatureGroup(name='Zone Markers', show=True).add_to(self.map)
        nametag_group = folium.FeatureGroup(name='Zone Names', show=True).add_to(self.map)

        for zone in zones:
            zone_icon = str(zone.points_per_hour)
            if zone.current_owner.name == 'l355':   # TODO: Implement properly!
                zone_color = '#1A9641'  # Green
            else:
                zone_color = '#D7191C'  # Red

            # Draw zone marker
            popup_html = f"""
                <div style="width: 300px;">
                    <h4>{zone.name}</h4>
                    <p>Points: <b>{zone.takeover_points} / +{zone.points_per_hour}</b></p>
                    <p>Value: {zone.value(date):.1f}</p>
                    <img style="max-width: 100%; height: auto; padding-top: 10px;"
                        src="https://warded.se/turf/img/zones/{zone.id}UTC.png">
                </div>
            """
            folium.Marker(
                location=zone.coordinate.as_list(),
                icon=plugins.BeautifyIcon(icon=zone_icon,
                                            icon_shape='circle',
                                            border_color=zone_color,
                                            text_color='black',
                                            background_color='white'),
                popup=folium.Popup(html=popup_html, offset=(2, 70)),
            ).add_to(marker_group)

            # Draw nametag
            nametag_html = f"""
            <div style="width: 150px; height: 30px; text-align: center;
                        line-height: 0.5; font-weight: bold;">
                <div style="height:30px; background-color: rgba(0, 0, 0, 0.5);
                            border-radius: 5px; padding: 5px;
                            color: white; display: inline-block;">
                    <p>{zone.name}</p>
                    <p>{zone.takeover_points} / +{zone.points_per_hour} (~{zone.value(date):.1f})</p>
                </div>
            </div>
            """
            folium.Marker(
                location=zone.coordinate.as_list(),
                icon=folium.DivIcon(icon_size=(150, 30),
                                    icon_anchor=(75, -15),
                                    html=nametag_html)
            ).add_to(nametag_group)


    def draw_graph(self, graph):
        graph_group = folium.FeatureGroup(name='Graph Lines', show=True).add_to(self.map)

        for node in graph.nodes:
            for edge in node.edges:
                start_coordinate = edge.start.zone.coordinate
                finish_coordinate = edge.finish.zone.coordinate
                halfway_coordinate = start_coordinate + (finish_coordinate - start_coordinate) / 2
                third_way_coordinate = start_coordinate + (finish_coordinate - start_coordinate) / 3

                folium.PolyLine([start_coordinate.as_list(), halfway_coordinate.as_list()], color='black', weight=2).add_to(graph_group)

                nametag_html = f"""
                    <div style="width: 30px; height: 20px; text-align: center;
                                line-height: 0.5; font-weight: bold; color: black;">
                        <p>{edge.cost:.2f}</p>
                    </div>
                """
                folium.Marker(
                    location=third_way_coordinate.as_list(),
                    icon=folium.DivIcon(icon_size=(30, 20),
                                        icon_anchor=(15, 10),
                                        html=nametag_html)
                ).add_to(graph_group)


    def draw_path(self, path_points):
        path_group = folium.FeatureGroup(name='Bike Path', show=True).add_to(self.map)
        folium.PolyLine(path_points, color='red', weight=4).add_to(path_group)


    def save_map(self, filename):
        folium.LayerControl().add_to(self.map)

        print('Saving map to', filename)
        self.map.save(filename)


'''
    def draw_map(self, m, area, graph, path):
        southWest = area['southWest']
        northEast = area['northEast']
        round_id = area['round_id']
        center = [(northEast[0] + southWest[0]) / 2, (northEast[1] + southWest[1]) / 2]

        # Create a map centered around a specific location

        # Create feature groups
        marker_group = folium.FeatureGroup(name='Zone Markers', show=True).add_to(m)
        nametag_group = folium.FeatureGroup(name='Zone Names', show=False).add_to(m)
        graph_group = folium.FeatureGroup(name='Graph Lines', show=False).add_to(m)
        radius_group = folium.FeatureGroup(name='Zone Radius', show=False).add_to(m)
        path_group = folium.FeatureGroup(name='Optimal Path', show=True).add_to(m)

        # Draw zones on the map
        for zone in area['zones']:
            self.draw_marker(area, zone, marker_group)
            self.draw_nametag(area, zone, nametag_group)
            self.draw_radius(zone, radius_group)

        # Add a bounding box to the map
        self.draw_bounding_box(area, m)

        # Draw graph connections
        self.draw_graph(graph, graph_group)
        self.draw_path(path, path_group)

        # Add layers
        folium.LayerControl().add_to(m)

        # Save the map to an HTML file
        m.save('maps/map_' + round_id + '.html')


    def draw_marker(area, zone, marker_group):
        zone_name = zone['name']
        zone_id = zone['id']
        lat = zone['latitude']
        lon = zone['longitude']
        tp = zone['takeoverPoints']
        pph = zone['pointsPerHour']

        value = zone['zone_data']['value']
        stdev_points = zone['zone_data']['stdev_points']
        zundin_url = zone['zone_data']['zundin_url']

        mean = area['mean_value']
        stdev = area['stdev_value']
        pts_diff = value - mean

        if value > mean + 2 * stdev:
            # Top 2.28%
            zone_icon = 's'
            zone_color = '#2B83BA'
        elif value > mean + stdev:
            # Top 15.87%
            zone_icon = 'a'
            zone_color = '#1A9641'
        elif value > mean:
            # Top 50%
            zone_icon = 'b'
            zone_color = '#A6D96A'
        elif value > mean - stdev:
            # Top 84.13%
            zone_icon = 'c'
            zone_color = '#FDAE61'
        elif value > mean - 2 * stdev:
            # Top 97.72%
            zone_icon = 'd'
            zone_color = '#D7191C'
        else:
            # Top 100%
            zone_icon = 'e'
            zone_color = '#000000'

        # Create marker
        popup_html = f"""
            <div style="width: 300px;">
                <h4>{zone_name}</h4>
                <p>Points: <b>{tp} / +{pph}</b></p>
                <p>
                    Value: <b>{value:.1f} ± {stdev_points:.1f}</b>
                    ({abs(pts_diff):.1f} {'above' if pts_diff > 0 else 'below'} average)
                </p>
                <a href="{zundin_url}">Full takeover log</a>
                <img style="max-width: 100%; height: auto; padding-top: 10px;"
                    src="https://warded.se/turf/img/zones/{zone_id}UTC.png">
            </div>
        """

        folium.Marker(
            location=[lat, lon],
            icon=plugins.BeautifyIcon(icon=zone_icon,
                                        icon_shape='circle',
                                        border_color=zone_color,
                                        text_color='black',
                                        background_color='white'),
            popup=folium.Popup(html=popup_html, offset=(2, 70)),
        ).add_to(marker_group)


    def draw_nametag(area, zone, nametag_group):
        zone_name = zone['name']
        lat = zone['latitude']
        lon = zone['longitude']
        value = zone['zone_data']['value']
        mean = area['mean_value']
        pts_diff = value - mean

        nametag_html = f"""
            <div style="width: 150px; height: 30px; text-align: center;
                        line-height: 0.5; font-weight: bold;">
                <div style="height:30px; background-color: rgba(0, 0, 0, 0.5);
                            border-radius: 5px; padding: 5px;
                            color: white; display: inline-block;">
                    <p>{zone_name}</p>
                    <p>{value:.1f} ({'+' if pts_diff > 0 else '-'}{abs(pts_diff):.1f})</p>
                </div>
            </div>
        """
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(icon_size=(150, 30),
                                icon_anchor=(75, -20),
                                html=nametag_html)
        ).add_to(nametag_group)


    def draw_radius(zone, radius_group):
        lat = zone['latitude']
        lon = zone['longitude']
        zone_radius = zone['zone_data']['value'] * GRAPH_CONNECTEDNESS

        # Draw circle shadow
        folium.Circle(
            location=[lat, lon],
            radius=zone_radius,
            color='black',
            fill=False,
            weight=2,
        ).add_to(radius_group)

        # Draw circle
        folium.Circle(
            location=[lat, lon],
            radius=zone_radius,
            color='red',
            fill=False,
            weight=2,
        ).add_to(radius_group)



    def draw_graph(graph, graph_group):
        i = 0
        for edge in graph.get_edges():
            # folium.PolyLine([edge.start.coords, edge.finish.coords], color='black', weight=2).add_to(graph_group)
            halfway_coords = [(edge.start.coords[0] + edge.finish.coords[0]) / 2, (edge.start.coords[1] + edge.finish.coords[1]) / 2]
            third_way_coords = [(edge.start.coords[0] + halfway_coords[0]) / 2, (edge.start.coords[1] + halfway_coords[1]) / 2]
            folium.PolyLine([edge.start.coords, edge.finish.coords], color='black', weight=2).add_to(graph_group)

            nametag_html = f"""
                <div style="width: 30px; height: 20px; text-align: center;
                            line-height: 0.5; font-weight: bold; color: black;">
                    <p>{edge.cost:.2f}</p>
                </div>
            """
            folium.Marker(
                location=third_way_coords,
                icon=folium.DivIcon(icon_size=(30, 20),
                                    icon_anchor=(15, 10),
                                    html=nametag_html)
            ).add_to(graph_group)

            i += 1

        print('Number of connections:', i)


    def draw_path(path, path_group):
        for node in path:
            edge = node.prev_edge
            if edge:
                # print('Node:', node.name, '- Drawing from', edge.start.name, 'to', edge.finish.name, 'with cost', edge.cost)
                folium.PolyLine([edge.start.coords, edge.finish.coords], color='red', weight=4).add_to(path_group)

'''