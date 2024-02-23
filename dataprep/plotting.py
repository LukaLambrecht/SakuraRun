###############################################
# Plot the locations of entries in a csv file #
###############################################


# imports
import os
import sys
import argparse
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
sys.path.append('..')
from tools.coordtools import df_to_coords


def plot_locations(coords):
    # make a visual representation of a set of coordinates
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # format coordinates
    lon = [float(coord['lon']) for coord in coords]
    lat = [float(coord['lat']) for coord in coords]
    # put coordinates in a dataframe
    df_coords = pd.DataFrame({'node': np.arange(len(coords))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    df_coords['color'] = 'red'
    df_coords['size'] = 1
    # plot the coordinates on map
    fig = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
                hover_data={'size':False, 'color':False, 'lat':True, 'lon':True},
                color='color', color_discrete_map='identity',
                size='size', size_max=10,
                zoom=8, height=600, width=900)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser(description='Plot locations of entries in a csv file')
    parser.add_argument('-i', '--inputfile', type=os.path.abspath)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--limit', default=500, type=int)
    args = parser.parse_args()

    # load input file
    df = pd.read_csv(args.inputfile, delimiter=args.delimiter)
    print('Read input file {} with {} entries.'.format(args.inputfile, len(df)))
    if len(df)>args.limit:
        msg = 'ERROR: number of entries exceeds limit ({})'.format(args.limit)
        raise Exception(msg)

    # get coordinates in suitable format
    coords = df_to_coords(df)

    # make a plot
    plot_locations(coords)
