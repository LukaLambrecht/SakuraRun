############################################################
# Cluster trees by categorical values in specified columns #
############################################################
# Typical use case: cluster all trees in the same street
# (assuming the dataframe contains a column specifying the street name).


# import external modules
import os
import sys
import argparse
import itertools
import pandas as pd
import numpy as np

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
topdir = os.path.abspath(os.path.join(thisdir, '../..'))
sys.path.append(topdir)

# local imports
from datatools.clustering.clustertools import split_cluster_by_max_distance
from datatools.clustering.cluster_dataset import cluster_parts


def cluster_categorical(
        df,
        column_names,
        num_key = None,
        lat_key = None,
        lon_key = None,
        max_distance = None,
        verbose = False):
    '''
    Cluster a dataframe by categorical values in specified columns.
    Input arguments:
    - df: pandas DataFrame.
    - column_names: list of names of the columns to cluster by.
      instances that have the same combination of values for each of the columns,
      will be clustered into one instance.
    - num_key: name of a new column to add to the clustered dataframe,
      specifying how many original instances were clustered into one.
    - lat_key, lon_key: name of the columns with latitude and longitude coordinates,
      used to determine the geographical cluster center.
    - max_distance: maximum distance between two instances in a cluster;
      bigger clusters will be split despite sharing the same categorical values.
    '''

    # check provided column names
    if column_names is None or len(column_names) == 0:
        msg = 'WARNING in cluster_categorical: received no column names to cluster by;'
        msg += ' skipping clustering and returning original dataframe.'
        print(msg)
        return df
    if isinstance(column_names, str): column_names = [column_names]
    for column_name in column_names:
        if column_name not in df.columns.values:
            msg = f'Column {column_name} not found in provided dataframe.'
            raise Exception(msg)

    # find values for each of the columns that are present in the dataframe
    column_values = {}
    for column_name in column_names:
        column_values[column_name] = sorted(list(set(df[column_name].values.astype(str))))
    if verbose:
        print('INFO in cluster_categorical: found following number of potential categories:')
        ncat = 1
        for k, v in column_values.items():
            print(f'  - column {k}: {len(v)} distinct values')
            ncat *= len(v)
        print(f'  --> {ncat} potential distinct categories')
        sys.stdout.flush()
        sys.stderr.flush()

    # split the data based on combination of values for each of the columns
    categories = []
    column_values_raw = [v for v in column_values.values()]
    for idx, value_combo in enumerate(itertools.product(*column_values_raw)):
        mask = np.ones(len(df)).astype(bool)
        for column_name, column_value in zip(column_names, value_combo):
            mask = ((mask) & (df[column_name].values.astype(str)==column_value))
        if np.sum(mask.astype(int))==0: continue
        part = df[mask]
        categories.append(part)
    if verbose:
        print(f'INFO in cluster_categorical: found {len(categories)} effective categories.')

    # check argument compatibility for max_distance
    if max_distance is not None and max_distance > 0:
        if lat_key is None or lon_key is None:
            msg = 'WARNING in cluster_categorical: max_distance was provided,'
            msg += ' but lat_key and lon_key were not specified;'
            msg += ' max_distance will be ignored.'
            print(msg)
            max_distance = None
            
    # perform additional splitting based on the maximum distance within each cluster
    if max_distance is not None and max_distance > 0:
        newcategories = []
        # loop over clusters
        for category in categories:
            # get coordinates in suitable format
            lats = category[lat_key].astype(float)
            lons = category[lon_key].astype(float)
            coords = [{'lon': lon, 'lat': lat} for lon, lat in zip(lons, lats)]
            # get indices of subclusters and add parts to total
            subcluster_sets = split_cluster_by_max_distance(coords, max_distance=max_distance)
            for subcluster_ids in subcluster_sets:
                newcategory = category.iloc[subcluster_ids]
                newcategories.append(newcategory)
        categories = newcategories
        if verbose:
            print('INFO in cluster_categorical: splitting clusters by distance threshold'
                  + f' resulted in {len(categories)} clusters.')

    # make the cluster centers
    centers = cluster_parts(categories, lat_key=lat_key, lon_key=lon_key, num_key=num_key)
    return centers


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--column_names', default=None, nargs='+')
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
    print('Column names:')
    print(list(dataset.columns.values))

    # do clustering
    centers = cluster_categorical(
      dataset,
      args.column_names,
      lat_key=args.lat_key,
      lon_key=args.lon_key,
      num_key=args.num_key,
      max_distance=args.max_distance,
      verbose=True
    )

    # write output file
    if args.outputfile is not None:
        centers.to_csv(args.outputfile, sep=args.delimiter, index=False)
