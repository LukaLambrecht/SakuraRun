########################################################################
# Tools for calculating and exporting the optimal route between points #
########################################################################
# This functionality uses the OSRM API
# see documentation here: https://project-osrm.org/
# more specifically here: https://project-osrm.org/docs/v5.24.0/api/#route-service

# Known issues
# - the 'profile' argument seems to be completely ignored in the url,
#   and always set to 'driving', which is not suitable for running...


# imports
import numpy as np
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import plotly.express as px


def make_osrm_route_url(source, dest, profile='foot'):
    # prepare the correct OSRM request URL
    # input arguments:
    # - source: coordinates of starting point, formatted as a string of the form "lon,lat"
    # - dest: coordinates of destination, formatted as a string of the form "lon,lat"
    # - profile: choose from "car", "bike" or "foot"
    url = 'http://router.project-osrm.org/route/v1/{}/'.format(profile)
    url += '{};{}?'.format(source, dest)
    url += 'alternatives=false&annotations=nodes'
    return url

def get_route_nodes(source, dest, **kwargs):
    # get nodes along the optimal route between source and destination
    # input arguments:
    # - source: coordinates of starting point, formatted as a string of the form "lon,lat"
    # - dest: coordinates of destination, formatted as a string of the form "lon,lat"
    # - kwargs: passed down to make_osrm_route_url
    url = make_osrm_route_url(source, dest, **kwargs)
    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers = headers)
    rjson = r.json()
    print(rjson)
    if rjson['code']!='Ok':
        msg = 'WARNING: request returned status code {}'.format(rjson['code'])
        print(msg)
    nodes = rjson['routes'][0]['legs'][0]['annotation']['nodes']
    return nodes

def nodes_to_coords(nodes, skip=None, verbose=False):
    # convert route nodes to coordinates
    # note: slow, check for optimizations
    if skip is not None: nodes = nodes[::skip]
    coords = []
    for node in nodes:
        try:
            url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
            headers = {'Content-type': 'application/json'}
            r = requests.get(url, headers=headers)
            myroot = ET.fromstring(r.text)
            for child in myroot:
                lat, lon = child.attrib['lat'], child.attrib['lon']
            coords.append('{},{}'.format(lon,lat))
        except:
            if verbose: print('WARNING: could not parse node to coordinates')
            continue
    return coords

def plot_route_nodes(source, dest, coords=None, nodes=None, **kwargs):
    # if no coordinates are provided, calculate them on the fly
    if coords is None:
        # if no nodes are provided, calculate them on the fly
        if nodes is None: nodes = get_route_nodes(source, dest, **kwargs)
        coords = nodes_to_coords(nodes, skip=3)
    # format coordinates
    lon = [float(coord.split(',')[0]) for coord in coords]
    lat = [float(coord.split(',')[1]) for coord in coords]
    # put coordinates in a dataframe
    df_coords = pd.DataFrame({'node': np.arange(len(coords))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    # plot the coordinates on map
    fig = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
            zoom=8, height=600, width=900)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


if __name__=='__main__':
    # testing section

    # define starting point and destination
    source = {'lat': 51.048903, 'lon': 3.695139}
    #dest = {'lat': 51.046213, 'lon': 3.698381}
    dest = {'lat': 51.052116, 'lon': 3.699504}

    # format
    start = "{},{}".format(source['lon'], source['lat'])
    end = "{},{}".format(dest['lon'], dest['lat'])

    # plot start to end
    plot_route_nodes(start, end)

    # plot end to start
    #plot_route_nodes(end, start)
