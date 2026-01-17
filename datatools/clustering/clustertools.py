############################
# Generic clustering tools #
############################

# import external modules
import os
import sys
import sklearn
import pandas as pd
import numpy as np

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
topdir = os.path.abspath(os.path.join(thisdir, '../..'))
sys.path.append(topdir)

# local imports
from python.distancematrix import get_geodesic_distance_matrix


def split_cluster_by_max_distance(
        coords,
        distance_matrix = None,
        max_distance = None,
        cids = None):
    '''
    Split a cluster of coordinates based on maximum allowed distance between any two points
    Input argument:
      - coords: list of dicts of the form {'lat': latitude, 'lon': longitude}
      - distance_matrix: distance matrix.
        if not provided, calculated on the fly (in geodesic approximation)
      - max_distance: maximum allowed distance (in meter) within each cluster
      - cids: for internal recursive calls only, do not use.
    Returns: lists of indices (w.r.t. input coords) of subclusters
    '''
    
    # calculate (simplified) distance matrix for original cluster
    if distance_matrix is None: distance_matrix = get_geodesic_distance_matrix(coords, verbose=False)
    (max1, max2) = np.unravel_index(np.argmax(distance_matrix, axis=None), distance_matrix.shape)
    maxdist = distance_matrix[max1, max2]

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
        dist_to_max1 = distance_matrix[idx, max1]
        dist_to_max2 = distance_matrix[idx, max2]
        if dist_to_max1 < dist_to_max2:
            cluster_1_ids.append(idx)
            cluster_1_orig_ids.append(cids[idx])
        else:
            cluster_2_ids.append(idx)
            cluster_2_orig_ids.append(cids[idx])
    cluster_1 = [coords[idx] for idx in cluster_1_ids]
    cluster_2 = [coords[idx] for idx in cluster_2_ids]
    distance_matrix_1 = distance_matrix[cluster_1_ids, :][:, cluster_1_ids]
    distance_matrix_2 = distance_matrix[cluster_2_ids, :][:, cluster_2_ids]

    # repeat recursively
    res1 = split_cluster_by_max_distance(
             cluster_1,
             distance_matrix = distance_matrix_1, 
             max_distance = max_distance,
             cids = cluster_1_orig_ids)
    res2 = split_cluster_by_max_distance(
             cluster_2,
             distance_matrix = distance_matrix_2,
             max_distance = max_distance,
             cids = cluster_2_orig_ids)

    return res1 + res2


def cluster_by_distance_threshold(
        coords,
        distance_matrix = None,
        distance_threshold = 1):
    '''
    Cluster a set of coordinates based on a preset distance threshold.
    Input argument:
      - coords: list of dicts of the form {'lat': latitude, 'lon': longitude}
      - distances: distance matrix.
        if not provided, calculated on the fly (in geodesic approximation).
      - distance_threshold: distance threshold (in meter) for clustering.
    Returns: lists of indices (w.r.t. input coords) of subclusters.
    '''

    # get distance matrix
    if distance_matrix is None: distance_matrix = get_geodesic_distance_matrix(coords)

    # make and run clusterer
    clusterer = sklearn.cluster.AgglomerativeClustering(
                  n_clusters = None,
                  distance_threshold = distance_threshold,
                  metric = 'precomputed',
                  linkage = 'complete')
    clusterer.fit(distance_matrix)
    cluster_labels = clusterer.labels_

    # convert cluster labels to cluster indices
    cluster_indices = []
    for label in np.unique(sorted(cluster_labels)):
        mask = (cluster_labels==label)
        cluster_indices.append(np.nonzero(mask))

    return cluster_indices
