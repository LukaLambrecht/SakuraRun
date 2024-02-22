import sys
import os
import numpy as np
import pandas as pd

import requests
import xml.etree.ElementTree as ET

import plotly.express as px


def make_osrm_url(start, end, service='route', transport='driving'):
    url = 'http://router.project-osrm.org/{}/v1/{}/'.format(service, transport)
    url += '{};{}?'.format(start, end)
    if service=='route': url += 'alternatives=false&annotations=nodes'
    return url

if __name__=='__main__':
    # see: https://medium.com/walmartglobaltech/
    # finding-and-plotting-optimal-route-using-open-source-api-in-python-cdcda596996c

    # define starting point and destination
    source = {'lat': 51.048903, 'lon': 3.695139}
    dest = {'lat': 51.046213, 'lon': 3.698381}

    # format
    start = "{},{}".format(source['lon'], source['lat'])
    end = "{},{}".format(dest['lon'], dest['lat'])

    # get route
    url = make_osrm_url(start, end, service='route', transport='walking')
    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers = headers)
    routejson = r.json()
    route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

    # get distance only
    url = make_osrm_url(start, end, service='table', transport='walking')
    r = requests.get(url, headers = headers)
    distance = r.json()
    print(distance)

    # convert route nodes to coordinates
    coordinates = []
    for node in route_nodes:
        try:
            url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
            r = requests.get(url, headers = headers)
            myroot = ET.fromstring(r.text)
            for child in myroot:
                lat, lon = child.attrib['lat'], child.attrib['lon']
            coordinates.append((lat, lon))
        except: continue
    print(coordinates[:10])

    # put coordinates in a dataframe
    df_out = pd.DataFrame({'Node': np.arange(len(coordinates))})
    df_out['coordinates'] = coordinates
    df_out[['lat', 'long']] = pd.DataFrame(df_out['coordinates'].tolist())
    df_out['lat'] = df_out['lat'].astype(float)
    df_out['long'] = df_out['long'].astype(float)

    # plot the coordinates on map
    color_scale = [(0, 'red'), (1,'green')]
    fig = px.scatter_mapbox(df_out,
                        lat="lat",
                        lon="long",
                        zoom=8,
                        height=600,
                        width=900)


    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
