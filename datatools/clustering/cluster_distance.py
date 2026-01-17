#################################################################
# Cluster trees that are very near to each other into one entry #
#################################################################
# Meant as a speedup for shortest path finder.


# import external modules
import os
import sys
import argparse
import pandas as pd
import numpy as np

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(thisdir, '..')))

# local imports
from python.distancematrix import get_geodesic_distance_matrix
from datatools.clustering.clustertools import cluster_by_distance_threshold
from datatools.clustering.cluster_dataset import cluster_by_indices


def cluster_distance(dataset,
        lat_key='lat', lon_key='lon', num_key='num',
        distance_threshold=1,
        verbose=False):
    
    # get coordinates in suitable format
    lats = dataset[lat_key].astype(float)
    lons = dataset[lon_key].astype(float)
    coords = [{'lon': lon, 'lat': lat} for lon, lat in zip(lons, lats)]

    # cluster by distance
    cluster_indices = cluster_by_distance_threshold(coords, distance_threshold=distance_threshold)

    # cluster dataset
    centers = cluster_by_indices(dataset, cluster_indices, lat_key=lat_key, lon_key=lon_key, num_key=num_key)

    # printouts
    if verbose:
        print('INFO in cluster_distance:')
        print(f'  - input instances: {len(dataset)}')
        print(f'  - clustered instances: {len(centers)}')
    return centers


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--lat_key', default='lat')
    parser.add_argument('--lon_key', default='lon')
    parser.add_argument('--num_key', default='num')
    parser.add_argument('--distance_threshold', default=1, type=float)
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    print('Column names:')
    print(dataset.columns)

    # do clustering
    centers = cluster_distance(
      dataset,
      lat_key=args.lat_key,
      lon_key=args.lon_key,
      num_key=args.num_key,
      distance_threshold=args.distance_threshold,
      verbose=True
    )

    # write output file
    if args.outputfile is not None:
        centers.to_csv(args.outputfile, sep=args.delimiter, index=False)
