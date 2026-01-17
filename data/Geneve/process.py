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
from datatools.clustering.cluster_distance import cluster_distance
from datatools.parsing.parse import parse
from datatools.selection.select_square import select_square
from tools.plottools import plot_locations

# local parsing import
from parse import parse_coords


if __name__=='__main__':

    # settings
    thisdir = os.path.dirname(os.path.abspath(__file__))
    inputfile = os.path.abspath(os.path.join(thisdir, 'raw/SIPV_ICA_ARBRE_ISOLE.csv'))
    outputfile = 'data-geneve-{}.csv'
    filters = [
      os.path.abspath(os.path.join(thisdir, 'filters/treetype_filter.json'))
    ]
    rename = {
      "NOM_COMPLET": "treetype"
    }
    clustering_distance_threshold = 100

    # load input file
    dataset = pd.read_csv(inputfile, sep=';')
    print('Loaded dataset {}'.format(inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    print('Column names:')
    print(dataset.columns.values)

    # filter
    dataset_filtered = filter_dataset(dataset, filters, verbose=True)

    # parse
    dataset_filtered = parse_coords(dataset_filtered)
    dataset_filtered = parse(dataset_filtered, rename=rename)

    # select region of interest
    dataset_selected = select_square(dataset_filtered,
                         lat_min = 46.195,
                         lat_max = 46.215,
                         lon_min = 6.125,
                         lon_max = 6.16,
                         verbose=True)

    # cluster
    dataset_clustered = cluster_distance(dataset_selected,
                          num_key='num',
                          distance_threshold=clustering_distance_threshold,
                          verbose=True)

    # plotting (filtered)
    lat = dataset_filtered['lat']
    lon = dataset_filtered['lon']
    extra_info = {}
    for key, val in dataset_filtered.items(): extra_info[key] = val.values
    plot_locations(lat, lon, extra_info=extra_info)

    # plotting (selected)
    lat = dataset_selected['lat']
    lon = dataset_selected['lon']
    extra_info = {}
    for key, val in dataset_selected.items(): extra_info[key] = val.values
    plot_locations(lat, lon, extra_info=extra_info)

    # plotting (clustered)
    lat = dataset_clustered['lat']
    lon = dataset_clustered['lon']
    extra_info = {}
    for key, val in dataset_clustered.items(): extra_info[key] = val.values
    plot_locations(lat, lon, extra_info=extra_info)

    # save output files
    dataset_filtered.to_csv(outputfile.format('filtered'), index=False)
    dataset_selected.to_csv(outputfile.format('selected'), index=False)
    dataset_clustered.to_csv(outputfile.format('clustered'), index=False)
