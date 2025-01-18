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


def plot_locations(lat, lon):
    # make a visual representation of a set of coordinates
    # input arguments:
    # - lat and lon: 1D numpy arrays with latitudes and longitudes
    
    # put coordinates in a dataframe
    df_coords = pd.DataFrame({'node': np.arange(len(lat))})
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
    parser.add_argument('--lat_key', default='lat')
    parser.add_argument('--lon_key', default='lon')
    args = parser.parse_args()

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    print('Column names:')
    print(dataset.columns)

    # check if maximum length is not exceeded
    if len(dataset)>args.limit:
        msg = 'ERROR: number of entries exceeds limit ({})'.format(args.limit)
        raise Exception(msg)

    # get coordinates
    lat = dataset[args.lat_key]
    lon = dataset[args.lon_key]

    # make a plot
    plot_locations(lat, lon)
