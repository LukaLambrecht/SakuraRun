###################################################
# Cluster trees in the same street into one entry #
###################################################
# Meant as a speedup for shortest path finder


import os
import sys
import argparse
import pandas as pd
import numpy as np


def cluster_streets(df, street_key, num_key=None, lat_key=None, lon_key=None):
    # return a dataframe with only cluster centers
    # (clustered per street name)

    # split the data based on street name
    streets = sorted(list(set(dataset[street_key])))
    datasets = []
    for street in streets:
        part = dataset[dataset[street_key]==street]
        datasets.append(part)
    print('Found {} clusters based on street name'.format(len(datasets)))

    # cluster each part
    centers = []
    for part in datasets:
        # copy first element of cluster
        center = part.iloc[[0]].copy()
        # average coordinates over cluster
        if lat_key is not None and lon_key is not None:
            lat_avg = np.average(part[lat_key])
            lon_avg = np.average(part[lon_key])
            center[lat_key] = lat_avg
            center[lon_key] = lon_avg
        # store number of trees clustered
        if num_key is not None:
            center[num_key] = len(part)
        centers.append(center)

    # combine cluster centers in a dataframe and return
    centers = pd.concat(centers, ignore_index=True)
    drop = [c for c in centers.columns if c.startswith('Unnamed:')]
    centers.drop(columns=drop, inplace=True)
    return centers


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--street_key', default='street')
    parser.add_argument('--lat_key', default='lat')
    parser.add_argument('--lon_key', default='lon')
    parser.add_argument('--num_key', default='num')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=',')
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    # do clustering
    centers = cluster_streets(
      dataset,
      args.street_key,
      lat_key=args.lat_key,
      lon_key=args.lon_key,
      num_key=args.num_key
    )

    # write output file
    if args.outputfile is not None:
        centers.to_csv(args.outputfile, sep=',')
