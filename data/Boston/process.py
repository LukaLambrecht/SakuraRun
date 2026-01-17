#!/usr/bin/env python3

############################
# Full processing sequence #
############################


import os
import sys
import pandas as pd

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(thisdir, '../..')))

# local imports
from datatools.filtering.filter import filter_dataset
from datatools.clustering.cluster_categorical import cluster_categorical
from datatools.parsing.parse import parse
from datatools.selection.select_square import select_square
from tools.plottools import plot_locations


if __name__=='__main__':

    # settings
    inputfiles = {
      'street': os.path.abspath(os.path.join(thisdir, 'raw/treekeeper_street_trees.csv')),
      'parks': os.path.abspath(os.path.join(thisdir, 'raw/treekeeper_parks_trees.csv'))
    }
    outputfile = 'data-boston-{}.csv'
    treetype_key = 'spp_bot'
    rename = {
      'spp_bot': 'treetype',
      'y_latitude': 'lat',
      'x_longitude': 'lon',
      'street': 'street',
      'park': 'street'
    }
    filters = [
      os.path.abspath(os.path.join(thisdir, 'filters/treetype_filter.json'))
    ]

    # load input files
    datasets = []
    for dtype, inputfile in inputfiles.items():
        
        dataset = pd.read_csv(inputfile)
        print('Loaded dataset {}'.format(inputfile))
        print('Number of entries: {}'.format(len(dataset)))
        print('Column names:')
        print(dataset.columns.values)

        # filter
        dataset_filtered = filter_dataset(dataset, filters, verbose=True)

        # parse
        dataset_filtered = parse(dataset_filtered, rename=rename)
        datasets.append(dataset_filtered)

    # merge
    dataset_filtered = pd.concat(datasets, ignore_index=True)

    # cluster
    dataset_clustered = cluster_categorical(dataset_filtered,
            column_names=['street'], num_key='num',
            verbose=True)

    # plotting (filtered)
    lat = dataset_filtered['lat']
    lon = dataset_filtered['lon']
    extra_info = {}
    for key, val in dataset_filtered.items(): extra_info[key] = val.values
    plot_locations(lat, lon, extra_info=extra_info)

    # plotting (clustered)
    lat = dataset_clustered['lat']
    lon = dataset_clustered['lon']
    extra_info = {}
    for key, val in dataset_clustered.items(): extra_info[key] = val.values
    plot_locations(lat, lon, extra_info=extra_info)

    # save output files
    dataset_filtered.to_csv(outputfile.format('filtered'), index=False)
    dataset_clustered.to_csv(outputfile.format('clustered'), index=False)
