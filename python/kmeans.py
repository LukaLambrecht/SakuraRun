#############################################################
# Tools for clustering coordinates using the k-means method #
#############################################################

import numpy as np
from sklearn.cluster import KMeans


def cluster_kmeans(coords, n_clusters=1):
    # partition a set of coordinates into clusters and calculate cluster centers

    # format input data
    X = np.zeros((len(coords), 2))
    for idx, coord in enumerate(coords):
        X[idx,0] = coord['lat']
        X[idx,1] = coord['lon']
    # do k-means
    kmeans = KMeans(n_clusters=n_clusters, n_init='auto')
    cluster_ids = kmeans.fit_predict(X)
    # partition input set
    coord_sets = []
    for cluster_idx in range(np.amin(cluster_ids), np.amax(cluster_ids)+1):
        ids = np.nonzero(cluster_ids==cluster_idx)[0]
        coord_set = [coords[idx] for idx in ids]
        coord_sets.append(coord_set)
    # get centroids
    cluster_centers = []
    for idx in range(len(kmeans.cluster_centers_)):
        cluster_centers.append({
            'lat': kmeans.cluster_centers_[idx, 0],
            'lon': kmeans.cluster_centers_[idx, 1]
        })
    return coord_sets, cluster_centers
