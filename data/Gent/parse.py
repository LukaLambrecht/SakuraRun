###############################################
# Parse the csv file to a conventional format #
###############################################


import numpy as np


def parse_coords(dataset):

    # write tree coordinates in a more conventional notation
    geo_points = dataset['geo_point_2d']
    lats = np.zeros(len(dataset))
    lons = np.zeros(len(dataset))
    for idx, geo_point in enumerate(geo_points):
        temp = geo_point.split(',')
        lat = float(temp[0])
        lon = float(temp[1])
        lats[idx] = lat
        lons[idx] = lon
    dataset['lat'] = lats
    dataset['lon'] = lons

    return dataset
