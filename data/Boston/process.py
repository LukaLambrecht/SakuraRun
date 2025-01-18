#!/usr/bin/env python3

############################
# Full processing sequence #
############################


import os
import sys
import pandas as pd


if __name__=='__main__':

    # settings
    thisdir = os.path.dirname(os.path.abspath(__file__))
    datatoolsdir = os.path.abspath(os.path.join(thisdir, '../../datatools'))
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
        cmd = 'python3 ' + os.path.join(datatoolsdir, 'filter.py')
        cmd += f' -i {inputfile}'
        cmd += f' -o {filtered}'
        cmd += f' --treetype_key {treetype_key}'
        cmd += f' --treetype_filter {treetype_filter}'
        os.system(cmd)

        # parse
        parsed = f'temp-2-{dtype}.csv'
        cmd = 'python3 parse.py'
        cmd += f' -i {filtered}'
        cmd += f' -o {parsed}'
        cmd += f' --dtype {dtype}'
        os.system(cmd)

    # add together
    dfs = []
    for dtype in inputfiles.keys():
        df = pd.read_csv(f'temp-2-{dtype}.csv', sep=',')
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    drop = [c for c in df.columns if c.startswith('Unnamed:')]
    df.drop(columns=drop, inplace=True)
    combined = 'temp-2.csv'
    df.to_csv(combined, sep=',')

    # select square
    selected = 'temp-3.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'select_square.py')
    cmd += f' -i {combined}'
    cmd += f' -o {selected}'
    #cmd += ' --lat_min {}'.format(41.813)
    #cmd += ' --lon_min {}'.format(-71.408)
    os.system(cmd)

    # cluster
    clustered = 'temp-4.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'cluster_streets.py')
    cmd += f' -i {selected}'
    cmd += f' -o {clustered}'
    os.system(cmd)

    # plotting
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {combined}'
    os.system(cmd)
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {clustered}'
    os.system(cmd)

    # output handling
    os.system(f'cp {clustered} {outputfile.format("processed")}')
    os.system(f'cp {selected} {outputfile.format("filtered-selected")}')
    os.system('rm *temp*.csv')
