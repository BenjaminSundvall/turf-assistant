import folium
import folium.plugins as plugins


TURF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
GRAPH_CONNECTEDNESS = 3


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


def draw_bounding_box(area, map):
    sw = area['southWest']
    ne = area['northEast']
    zone_count = len(area['zones'])
    round_id = area['round_id']

    # Draw bounding box
    folium.Rectangle(
        bounds=[sw, ne],
        color='blue',
        fill=False,
    ).add_to(map)

    # Add text box
    text = f"""
        <div style="background-color: white; padding: 10px; border: 1px solid black;">
            <p>{zone_count} zones</p>
            <p>Round {round_id}</p>
        </div>
    """
    folium.Marker(
        sw,
        icon=folium.features.DivIcon(
            icon_size=(150,36),
            icon_anchor=(0,0),
            html=text,
        )
    ).add_to(map)


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


def draw_map(area, graph, path):
    southWest = area['southWest']
    northEast = area['northEast']
    round_id = area['round_id']
    center = [(northEast[0] + southWest[0]) / 2, (northEast[1] + southWest[1]) / 2]

    # Create a map centered around a specific location
    m = folium.Map(location=center, zoom_start=14)

    # Create feature groups
    marker_group = folium.FeatureGroup(name='Zone Markers', show=True).add_to(m)
    nametag_group = folium.FeatureGroup(name='Zone Names', show=False).add_to(m)
    graph_group = folium.FeatureGroup(name='Graph Lines', show=False).add_to(m)
    radius_group = folium.FeatureGroup(name='Zone Radius', show=False).add_to(m)
    path_group = folium.FeatureGroup(name='Optimal Path', show=True).add_to(m)

    # Draw zones on the map
    for zone in area['zones']:
        draw_marker(area, zone, marker_group)
        draw_nametag(area, zone, nametag_group)
        draw_radius(zone, radius_group)

    # Add a bounding box to the map
    draw_bounding_box(area, m)

    # Draw graph connections
    draw_graph(graph, graph_group)
    draw_path(path, path_group)

    # Add layers
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    m.save('maps/map_' + round_id + '.html')

