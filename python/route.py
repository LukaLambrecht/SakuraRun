###################################################################
# Tools for calculating the optimal route between a set of points #
###################################################################
# This functionality uses the GraphHopper API
# see documentation here: https://www.graphhopper.com/
# more specifically here: https://docs.graphhopper.com/#operation/postRoute


# external imports
import os
import sys
import json
import math
import numpy as np
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(thisdir, '..')))

# import GraphHopper API key
from api.api_key import API_KEY

# local imports
from api.requests import graphhopper_request


def get_route_coords(coords, session=None, profile='foot', chunksize=None):
    # get the route between a set of coordinates
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - session: requests.Session object (if None, a new one is created)
    # - profile: mode of transport, choose from 'car', 'bike' or 'foot'
    # - chunksize: number of coordinates to put in one chunk, i.e. one API call
    #   (default: do not split in chunks, make one API call for the full coords list)
    #   (use chunksize = 5 or lower to be compatible with a free GraphHopper account)
    # returns:
    #   list of coordinates in same format as input
    if session is None: session = requests.Session()
    
    if( chunksize is not None and len(coords)>chunksize ):
        chunksize = int(chunksize)-1
        nchunks = int(math.ceil((len(coords)-1)/chunksize))
        # (note: -1 is because chunks must be overlapping by one point)
        routecoords = []
        routeinfo = {'distance': 0.}
        counter = 0
        for i in range(0, len(coords)-1, chunksize):
            # print counter
            counter += 1
            msg =''
            if counter>1: msg += '\033[F'
            msg += 'Calculating route chunk {} of {}...'.format(counter,nchunks)
            print(msg)
            # make chunk and calculate route for this chunk
            chunk = coords[i:i+chunksize+1]
            chunkcoords, chunkinfo = get_route_coords(chunk,
                    session=session, profile=profile)
            # aggregate results
            routecoords += chunkcoords
            routeinfo['distance'] += chunkinfo['distance']
        return (routecoords, routeinfo)
    
    else:
        points = [[el['lon'], el['lat']] for el in coords]
        json = {
          'profile': profile,
          'points': points,
          'instructions': False,
          'points_encoded': False
        } 
        response = graphhopper_request(session, json, API_KEY, service='route')
        points = np.array(response['paths'][0]['points']['coordinates'])
        coords = [{'lon': el[0], 'lat': el[1]} for el in points]
        distance = response['paths'][0]['distance']
        info = {'distance': distance}
        return (coords, info)


def plot_route_coords(coords, route_coords=None, **kwargs):
    # make a visual representation of the route
    # if no route is provided, calculate it on the fly
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - route_coords: route between coords, in same format as coords
    # - kwargs: passed down to get_route_coords if needed
    if route_coords is None: route_coords = get_route_coords(coords, **kwargs)[0]
    # put coordinates in a dataframe
    lon = [float(coord['lon']) for coord in coords]
    lat = [float(coord['lat']) for coord in coords]
    df_coords = pd.DataFrame({'node': np.arange(len(coords))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    df_coords['color'] = 'red'
    df_coords['size'] = 1
    # put route in a dataframe
    lon = [float(coord['lon']) for coord in route_coords]
    lat = [float(coord['lat']) for coord in route_coords]
    df_route = pd.DataFrame({'node': np.arange(len(route_coords))})
    df_route['lat'] = lat
    df_route['lon'] = lon
    df_route['color'] = 'blue'
    # plot the coordinates on map
    fig1 = px.line_mapbox(df_route, lat="lat", lon="lon",
             color='color', color_discrete_map='identity',
             zoom=8, height=600, width=900)
    fig2 = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
             hover_data={'size':False, 'lat':True, 'lon':True},
             color='color', color_discrete_map='identity',
             size='size', size_max=10,
             zoom=8, height=600, width=900)
    fig = go.Figure(data=fig1.data+fig2.data)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
