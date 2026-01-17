###############################################
# Parse the csv file to a conventional format #
###############################################


import os
import sys
import argparse
import pandas as pd
import numpy as np


def parse_coords(dataset):

    # get the coordinates
    addresses = dataset['Property Address']
    lats = np.zeros(len(dataset))
    lons = np.zeros(len(dataset))
    mask = np.ones(len(dataset)).astype(bool)
    nwarnings = 0
    for idx, address in enumerate(addresses):
        try:
            temp = address.split('(')[1].strip(' \n\t()')
            temp = temp.split(',')
            lat = float(temp[0].strip(' '))
            lon = float(temp[1].strip(' '))
        except:
            msg = 'WARNING: could not parse the coordinates'
            msg += f' for address "{address}".'
            print(msg)
            # do do: use graphhopper api to find coordinates
            nwarnings += 1
            lat = None
            lon = None
            mask[idx] = False
        lats[idx] = lat
        lons[idx] = lon
    msg = 'WARNING: could not parse the coordinates'
    msg += f' for {nwarnings} out of {len(dataset)} entries.'
    print(msg)
    dataset['lat'] = lats
    dataset['lon'] = lons
    dataset = dataset[mask]

    return dataset
