#!/usr/bin/env python3

############################
# Full processing sequence #
############################


import os
import sys
import pandas as pd

thisdir = os.path.dirname(os.path.abspath(__file__))
topdir = os.path.abspath(os.path.join(thisdir, '../../'))
sys.path.append(topdir)

from datatools.filter import filter_dataset
from datatools.select_square import select_square
#from datatools.cluster_streets import cluster_streets
from datatools.plot_locations import plot_locations
from data.Boston.parse import parse_dataset


if __name__=='__main__':

    # settings
    inputfiles = {
      'street': os.path.abspath(os.path.join(thisdir, 'raw/treekeeper_street_trees.csv')),
      'parks': os.path.abspath(os.path.join(thisdir, 'raw/treekeeper_parks_trees.csv'))
    }
    outputfile = 'data-boston-{}.csv'
    treetype_key = 'spp_bot'
    treetype_filter = os.path.abspath(os.path.join(thisdir, 'filters/treetype_filter.json'))

    for dtype, inputfile in inputfiles.items():
    
        # filter
        filtered = f'temp-1-{dtype}.csv'
        df = pd.read_csv(inputfile, sep=',')
        filtered_df = filter_dataset(df,
          treetype_key=treetype_key, treetype_filter=treetype_filter)
        filtered_df.to_csv(filtered, sep=',', index=False)
    
        # parse
        parsed = f'temp-2-{dtype}.csv'
        df = pd.read_csv(filtered, sep=',')
        parsed_df = parse_dataset(df, dtype=dtype)
        parsed_df.to_csv(parsed, sep=',', index=False)

    # add together
    dfs = []
    for dtype in inputfiles.keys():
        df = pd.read_csv(f'temp-2-{dtype}.csv', sep=',')
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    drop = [c for c in combined_df.columns if c.startswith('Unnamed:')]
    combined_df.drop(columns=drop, inplace=True)
    combined = 'temp-2.csv'
    combined_df.to_csv(combined, sep=',')

    # select square
    selected = 'temp-3.csv'
    df = pd.read_csv(combined, sep=',')
    selected_df = select_square(df)
    selected_df.to_csv(selected, sep=',', index=False)

    # cluster
    #clustered = 'temp-4.csv'
    #df = pd.read_csv(selected, sep=',')
    #clustered_df = cluster_streets(df)
    #clustered_df.to_csv(clustered, sep=',', index=False)

    # plotting
    plot_locations(combined_df['lat'], combined_df['lon'])
    #plot_locations(clustered_df['lat'], clustered_df['lon'])

    # output handling
    #os.system(f'cp {clustered} {outputfile.format("processed")}')
    #os.system(f'cp {selected} {outputfile.format("filtered-selected")}')
    os.system('rm *temp*.csv')
