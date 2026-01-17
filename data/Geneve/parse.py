###############################################
# Parse the csv file to a conventional format #
###############################################


import os
import sys
import pyproj
import argparse
import pandas as pd
import numpy as np


def parse_coords(dataset):
    # parse tree coordinates
    # the latitude and longitude are stored in some weird custom coordinate system;
    # need to convert using pyproj package
    lats = np.zeros(len(dataset))
    lons = np.zeros(len(dataset))
    ns = dataset['N'].values
    es = dataset['E'].values
    transformer = pyproj.Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
    for idx in range(len(dataset)):
        n = ns[idx]
        e = es[idx]
        lon, lat = transformer.transform(e, n)
        lats[idx] = lat
        lons[idx] = lon
    dataset['lat'] = lats
    dataset['lon'] = lons

    return dataset
