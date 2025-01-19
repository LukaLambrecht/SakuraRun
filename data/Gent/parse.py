###############################################
# Parse the csv file to a conventional format #
###############################################


import os
import sys
import argparse
import pandas as pd
import numpy as np


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=';')
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    # rename columns
    rename = {
      'sortiment': 'treetype',
      'straatnaam': 'street',
      'onderhoudsgebied': 'area'
    }
    dataset.rename(columns=rename, inplace=True)

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

    # remove unneeded columns
    keep = list(rename.values()) + ['lat', 'lon']
    drop = [c for c in dataset.columns if c not in keep]
    dataset.drop(columns=drop, inplace=True)

    # write to output file
    if args.outputfile is not None:
        dataset.to_csv(args.outputfile, sep=',', index=False)
