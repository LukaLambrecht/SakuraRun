#################################################################
# Cluster trees that are very near to each other into one entry #
#################################################################
# Meant as a speedup for shortest path finder.


# import external modules
import os
import sys
import argparse
import sklearn
import pandas as pd
import numpy as np

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(thisdir, '..')))

# local imports
from python.distancematrix import get_geodesic_distance_matrix
from datatools.cluster_dataset import cluster_by_label


def cluster_distance(dataset,
        lat_key='lat', lon_key='lon', num_key='num',
        threshold_distance=1,
        verbose=False):
    
    # get coordinates in suitable format
    lats = dataset[lat_key].astype(float)
    lons = dataset[lon_key].astype(float)
    coords = [{'lon': lon, 'lat': lat} for lon, lat in zip(lons, lats)]

    # get distance matrix and min/max distance between points
    distance_matrix = get_geodesic_distance_matrix(coords)
    dm_flat = distance_matrix.flatten()
    min_distance = np.amin(dm_flat[np.nonzero(dm_flat)])
    max_distance = np.amax(dm_flat)

    # make and run clusterer
    clusterer = sklearn.cluster.AgglomerativeClustering(
                  n_clusters=None,
                  distance_threshold=threshold_distance,
                  metric='precomputed',
                  linkage='complete')
    clusterer.fit(distance_matrix)
    cluster_labels = clusterer.labels_

    # cluster dataset
    centers = cluster_by_label(dataset, cluster_labels, lat_key=lat_key, lon_key=lon_key, num_key=num_key)

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
    parser.add_argument('--threshold_distance', default=1, type=float)
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    # do clustering
    centers = cluster_distance(
      dataset,
      lat_key=args.lat_key,
      lon_key=args.lon_key,
      num_key=args.num_key,
      threshold_distance=args.threshold_distance,
      verbose=True
    )

    # write output file
    if args.outputfile is not None:
        centers.to_csv(args.outputfile, sep=args.delimiter, index=False)
