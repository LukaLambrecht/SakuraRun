###################################
# Tools for coordinate conversion #
###################################


import numpy as np
import pandas as pd


def df_to_coords(df):
    # custom conversion function
    # input: a dataframe in the Ghent trees open data format
    # output: list of coordinates formatted as {'lon': longitude, 'lat': latitude}
    coords = df['geo_point_2d']
    coords = [coord.split(',') for coord in coords]
    coords = [{'lon': float(coord[1]), 'lat': float(coord[0])} for coord in coords]
    return coords
