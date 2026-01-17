##################################
# Tools for clustering a dataset #
##################################

import os
import sys
import numpy as np
import pandas as pd


def make_cluster_center(cluster, lat_key='lat', lon_key='lon', num_key='num'):
    # compress a given dataset (assumed to represent a single cluster)
    # into a single entry (representing the center of the cluster)
    
    # copy first element of cluster
    center = cluster.iloc[[0]].copy()
    # average coordinates over cluster
    if lat_key is not None and lon_key is not None:
        lat_avg = np.average(cluster[lat_key])
        lon_avg = np.average(cluster[lon_key])
        center[lat_key] = lat_avg
        center[lon_key] = lon_avg
    # store number of trees clustered
    if num_key is not None:
        center[num_key] = len(cluster)
    return center


def cluster_parts(parts, **kwargs):
    centers = []
    for part in parts:
        centers.append(make_cluster_center(part, **kwargs))
    centers = pd.concat(centers, ignore_index=True)
    return centers


def cluster_by_indices(dataset, cluster_indices, **kwargs):
    parts = []
    for indices in cluster_indices: parts.append(dataset.iloc[indices])
    return cluster_parts(parts)


def cluster_by_label(dataset, cluster_labels, **kwargs):
    indices = []
    for label in np.unique(sorted(cluster_labels)):
        mask = (cluster_labels==label)
        indices.append(np.nonzero(mask))
    return cluster_by_indices(dataset, indices, **kwargs)
