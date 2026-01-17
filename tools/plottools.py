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


def plot_locations(lat, lon, extra_info=None):
    # make a visual representation of a set of coordinates
    # input arguments:
    # - lat and lon: 1D numpy arrays with latitudes and longitudes
    
    # put coordinates in a dataframe
    df_coords = pd.DataFrame({'node': np.arange(len(lat))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    df_coords['color'] = 'red'
    df_coords['size'] = 1
    if extra_info is not None:
        for key, val in extra_info.items():
            df_coords[key] = val

    # define what to display on hovering
    hover_data = {'size':False, 'color':False, 'lat':True, 'lon':True}
    if extra_info is not None:
        for key in extra_info.keys(): hover_data[key] = True
    
    # plot the coordinates on map
    fig = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
                hover_data=hover_data,
                color='color', color_discrete_map='identity',
                size='size', size_max=10,
                zoom=8, height=600, width=900)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
