###############################################
# Parse the csv file to a conventional format #
###############################################


import os
import sys
import pyproj
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
      'NOM_COMPLET': 'treetype',
    }
    dataset.rename(columns=rename, inplace=True)

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

    # remove unneeded columns
    keep = list(rename.values()) + ['lat', 'lon']
    drop = [c for c in dataset.columns if c not in keep]
    dataset.drop(columns=drop, inplace=True)

    # write to output file
    if args.outputfile is not None:
        dataset.to_csv(args.outputfile, sep=',', index=False)
