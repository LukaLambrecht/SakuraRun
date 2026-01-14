###################################################
# Cluster trees in the same street into one entry #
###################################################
# Meant as a speedup for shortest path finder


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
from datatools.cluster_dataset import cluster_parts


def split_cluster(coords, distances=None, max_distance=None, cids=None):
    # split a cluster of coordinates based on maximum allowed distance between any two points
    # input argument:
    # - coords: list of dicts of the form {'lat': latitude, 'lon': longitude}
    # - distances: distance matrix.
    #   if not provided, calculated on the fly (in geodesic approximation)
    # - max_distance: maximum allowed distance (in meter) within each cluster
    # - cids: for internal recursive calls only, do not use.
    # returns: lists of indices (w.r.t. input coords) of subclusters
    
    # calculate (simplified) distance matrix for original cluster
    if distances is None: distances = get_geodesic_distance_matrix(coords, verbose=False)
    (max1, max2) = np.unravel_index(np.argmax(distances, axis=None), distances.shape)
    maxdist = distances[max1, max2]

    # handle case where no splitting is needed
    if cids is None: cids = list(range(len(coords)))
    if maxdist is None: return [cids]
    if maxdist < max_distance: return [cids]

    # split into two clusters by max distance
    cluster_1_ids = [max1]
    cluster_2_ids = [max2]
    cluster_1_orig_ids = [cids[max1]]
    cluster_2_orig_ids = [cids[max2]]
    for idx in range(len(coords)):
        if idx == max1 or idx == max2: continue
        dist_to_max1 = distances[idx, max1]
        dist_to_max2 = distances[idx, max2]
        if dist_to_max1 < dist_to_max2:
            cluster_1_ids.append(idx)
            cluster_1_orig_ids.append(cids[idx])
        else:
            cluster_2_ids.append(idx)
            cluster_2_orig_ids.append(cids[idx])
    cluster_1 = [coords[idx] for idx in cluster_1_ids]
    cluster_2 = [coords[idx] for idx in cluster_2_ids]
    distances_1 = distances[cluster_1_ids, :][:, cluster_1_ids]
    distances_2 = distances[cluster_2_ids, :][:, cluster_2_ids]

    # repeat recursively
    res1 = split_cluster(cluster_1, distances=distances_1, max_distance=max_distance,
            cids=cluster_1_orig_ids)
    res2 = split_cluster(cluster_2, distances=distances_2, max_distance=max_distance,
            cids=cluster_2_orig_ids)
    return res1 + res2


def cluster_streets(df, street_key, num_key=None, lat_key=None, lon_key=None, max_distance=None):
    # return a dataframe with only cluster centers
    # (clustered per street name)

    # split the data based on street name
    print('Performing clustering by street name...')
    streets = sorted(list(set(df[street_key])))
    datasets = []
    for street in streets:
        part = df[df[street_key]==street]
        datasets.append(part)
    print('Found {} clusters based on street name'.format(len(datasets)))

    # check argument compatibility for max_distance
    if max_distance is not None and max_distance > 0:
        if lat_key is None or lon_key is None:
            msg = 'WARNING: if you specify a max_distance to cluster_streets,'
            msg += ' lat_key and lon_key cannot be None;'
            msg += ' max_distance will be ignored.'
            print(msg)
            max_distance = None
            
    # perform additional splitting based on the maximum distance within each cluster
    if max_distance is not None and max_distance > 0:
        print(f'Performing cluster splitting with maximum distance {max_distance}...')
        newparts = []
        # loop over clusters
        for part in datasets:
            # get coordinates in suitable format
            lats = part[lat_key].astype(float)
            lons = part[lon_key].astype(float)
            coords = [{'lon': lon, 'lat': lat} for lon, lat in zip(lons, lats)]
            # get indices of subclusters and add parts to total
            subcluster_sets = split_cluster(coords, max_distance=max_distance)
            for subcluster_ids in subcluster_sets:
                newpart = part.iloc[subcluster_ids]
                newparts.append(newpart)
        datasets = newparts
        print(f'Splitting resulted in {len(datasets)} clusters.')

    # make the cluster centers
    centers = cluster_parts(datasets, lat_key=lat_key, lon_key=lon_key, num_key=num_key)
    return centers


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--street_key', default='street')
    parser.add_argument('--lat_key', default='lat')
    parser.add_argument('--lon_key', default='lon')
    parser.add_argument('--num_key', default='num')
    parser.add_argument('--max_distance', default=-1, type=float)
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
    centers = cluster_streets(
      dataset,
      args.street_key,
      lat_key=args.lat_key,
      lon_key=args.lon_key,
      num_key=args.num_key,
      max_distance=args.max_distance
    )

    # write output file
    if args.outputfile is not None:
        centers.to_csv(args.outputfile, sep=args.delimiter, index=False)
