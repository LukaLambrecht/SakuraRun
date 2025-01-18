################################################################
# Tools for building a distance matrix between a set of points #
################################################################
# This functionality uses the GraphHopper API
# see documentation here: https://www.graphhopper.com/
# more specifically here: https://docs.graphhopper.com/#operation/postMatrix


# external imports
import os
import sys
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


def get_distance_matrix(coords,
        session=None,
        profile='foot',
        blocksize=None,
        geodesic=False,
        to_coords=None):
    # get the distance matrix between a set of coordinates
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - session: requests.Session object (if None, a new one is created)
    # - profile: mode of transport, choose from 'car', 'bike' or 'foot'
    # - blocksize: specify the splitting of the API calls
    #   - None (default): make a single API call for the full matrix of points
    #     (with a free GraphHopper account, this method is limited to 5 points)
    #   - integer n > 2 and < len(coords): split the API call in blocks of n points
    #     (works with a free GraphHoper account if n <= 5, but can be slow)
    #   - 2: make a separate api call for each pair of points
    #     (works with a free GraphHopper account but is very slow,
    #     especially since frequent pauses are needed to replenish the minutely quotum)
    # - geodesic: get simple geodesic distance matrix.
    #   this is a lot faster for large coordinate collections
    #   and does not use GraphHopper, but might be inaccurate (e.g. crossing rivers).
    # - to_coords: currently only for internal use, do not call.
    # returns:
    #   numpy array with distances in meter;
    #   d[i,j] gives the distances between the i'th point as source
    #   and the j'th point as destination

    # first handle case of geodesic distance matrix
    # (does not need a request session)
    if geodesic: return get_geodesic_distance_matrix(coords)

    if session is None: session = requests.Session()
    
    if( isinstance(blocksize,int) and blocksize==2 ):
        # initialize output array
        distances = np.zeros((len(coords),len(coords)))
        # loop over pairs of points
        npairs = int(len(coords)*(len(coords)-1)/2)
        counter = 0
        for i in range(len(coords)):
            for j in range(i+1, len(coords)):
                # print counter
                counter += 1
                msg =''
                if counter>1: msg += '\033[F'
                msg += 'Calculating distance matrix pair {} of {}...'.format(counter,npairs)
                print(msg)
                # find pair of coordinates
                thiscoords = [coords[i], coords[j]]
                # calculate distance between two points
                temp = get_distance_matrix(thiscoords,
                        session=session, profile=profile)
                distances[i,j] = temp[0,1]
                distances[j,i] = temp[1,0]
        return distances
    
    elif( isinstance(blocksize,int) and blocksize>2 and blocksize<len(coords) ):
        # initialize output array
        distances = np.zeros((len(coords),len(coords)))
        # loop over pairs of blocks
        nblocks1d = math.ceil(len(coords)/blocksize)
        nblocks = int(nblocks1d*(nblocks1d+1)/2)
        counter = 0
        for i in range(0, len(coords), blocksize):
            for j in range(i, len(coords), blocksize):
                # print counter
                counter += 1
                msg =''
                if counter>1: msg += '\033[F'
                msg += 'Calculating distance matrix block {} of {}...'.format(counter,nblocks)
                print(msg)
                # get block coordinates
                from_coords = coords[i:i+blocksize]
                to_coords = coords[j:j+blocksize]
                # calculate distance between blocks of points
                temp = get_distance_matrix(from_coords,
                        session=session, profile=profile,
                        to_coords=to_coords)
                distances[i:i+blocksize,j:j+blocksize] = temp
                distances[j:j+blocksize,i:i+blocksize] = temp.transpose()
        return distances
    
    elif( blocksize is None ):
        points = [[el['lon'], el['lat']] for el in coords]
        json = {
          'profile': profile,
          'points': points,
          'instructions': False,
          'points_encoded': False,
          'out_arrays': ['distances']
        }
        if to_coords is not None:
            to_points = [[el['lon'], el['lat']] for el in to_coords]
            json.pop('points')
            json['from_points'] = points
            json['to_points'] = to_points
        response = graphhopper_request(session, json, API_KEY, service='matrix')
        distances = np.array(response['distances'])
        return distances
    
    else:
        msg = 'ERROR: blocksize {} (type {}) not recognized;'.format(blocksize, type(blocksize))
        msg += ' must be an integer between 2 and {} or None.'.format(len(coords))
        raise Exception(msg)


def get_geodesic_distance_matrix(coords):
    # get simple geodesic distance matrix
    def distance(lat1, lon1, lat2, lon2):
        r = 6371000 # (in meter)
        p = math.pi / 180.
        a = ( 0.5 - math.cos((lat2-lat1)*p)/2.
              + math.cos(lat1*p) * math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p))/2. )
        return 2 * r * math.asin(math.sqrt(a))
    size = len(coords)
    distances = np.zeros((size, size))
    ncalls = int(size*(size-1)/2)
    counter = 0
    for idx1 in range(size):
        for idx2 in range(idx1+1, size):
            dist = distance(coords[idx1]['lat'], coords[idx2]['lon'], coords[idx2]['lat'], coords[idx2]['lon'])
            distances[idx1, idx2] = dist
            distances[idx2, idx1] = dist
            counter += 1
            completion = 100*float(counter)/ncalls
            print('Calculating distance matrix: {:.2f}%'.format(completion), end='\r')
    print('Calculating distance matrix: {:.2f}%'.format(completion))
    return distances


def plot_distance_matrix(coords, distances=None, **kwargs):
    # make a visual representation of the distance matrix
    # if no distances are provided, calculate them on the fly
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - distances: distance matrix in np array format (e.g. output of get_distance_matrix)
    # - kwargs: passed down to get_distance_matrix if needed
    if distances is None: distances = get_distances_matrix(coords, **kwargs)
    # format coordinates
    lon = [float(coord['lon']) for coord in coords]
    lat = [float(coord['lat']) for coord in coords]
    # put coordinates in a dataframe
    df_coords = pd.DataFrame({'node': np.arange(len(coords))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    df_coords['color'] = 'red'
    df_coords['size'] = 1
    # put connecting lines in a list of dataframes
    # note: differences between i,j and j,i are ignored for now
    dfs = []
    for i in range(distances.shape[0]):
        for j in range(i+1,distances.shape[1]):
            df = pd.DataFrame({'note': np.arange(2)})
            df['lat'] = [lat[i], lat[j]]
            df['lon'] = [lon[i], lon[j]]
            dfs.append(df)
    # make a dataframe with transparent points along the edges for displaying text
    df_text = pd.DataFrame({'node': np.arange(len(dfs))})
    mid_lat = []
    mid_lon = []
    mid_dist = []
    for i in range(distances.shape[0]):
        for j in range(i+1,distances.shape[1]):
            mid_lat.append( (lat[i]+lat[j])/2. )
            mid_lon.append( (lon[i]+lon[j])/2. )
            mid_dist.append(distances[i,j])
    df_text['lat'] = mid_lat
    df_text['lon'] = mid_lon
    df_text['size'] = 1
    df_text['distance'] = mid_dist
    # plot the coordinates on map
    tempfig = px.scatter_mapbox(df_text, lat="lat", lon="lon",
                hover_data={'distance': True, 'size':False, 'lat':False, 'lon':False},
                size='size', size_max=10)
    figdata = tempfig.data
    for df in dfs:
        tempfig = px.line_mapbox(df, lat="lat", lon="lon")
        figdata += tempfig.data
    tempfig = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
                hover_data={'size':False, 'color':False, 'lat':True, 'lon':True},
                color='color', color_discrete_map='identity',
                size='size', size_max=10,
                zoom=8, height=600, width=900)
    figdata += tempfig.data
    fig = go.Figure(figdata)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
