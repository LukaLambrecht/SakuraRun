#!/usr/bin/env python3

############################
# Full processing sequence #
############################


import os
import sys


if __name__=='__main__':

    # settings
    thisdir = os.path.dirname(os.path.abspath(__file__))
    datatoolsdir = os.path.abspath(os.path.join(thisdir, '../../datatools'))
    inputfile = os.path.abspath(os.path.join(thisdir, 'raw/Providence_Tree_Inventory_20250118.csv'))
    outputfile = 'data-providence-{}.csv'
    treetype_key = 'Species'
    treetype_filter = os.path.abspath(os.path.join(thisdir, 'filters/treetype_filter.json'))
    max_cluster_distance = 100

    # filter
    filtered = 'temp-1.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'filter.py')
    cmd += f' -i {inputfile}'
    cmd += f' -o {filtered}'
    cmd += f' --treetype_key {treetype_key}'
    cmd += f' --treetype_filter {treetype_filter}'
    print('--- Running filtering ---')
    os.system(cmd)

    # parse
    parsed = 'temp-2.csv'
    cmd = 'python3 parse.py'
    cmd += f' -i {filtered}'
    cmd += f' -o {parsed}'
    print('--- Running parsing ---')
    os.system(cmd)

    # select square
    selected = 'temp-3.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'select_square.py')
    cmd += f' -i {parsed}'
    cmd += f' -o {selected}'
    cmd += ' --lat_min {}'.format(41.813)
    cmd += ' --lat_max {}'.format(41.839)
    cmd += ' --lon_min {}'.format(-71.408)
    print('--- Running square selection ---')
    os.system(cmd)

    # cluster
    clustered = 'temp-4.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'cluster_streets.py')
    cmd += f' -i {selected}'
    cmd += f' -o {clustered}'
    cmd += f' --max_distance {max_cluster_distance}'
    print('--- Running clustering ---')
    os.system(cmd)

    # plotting
    print('--- Running plotting ---')
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {parsed}'
    os.system(cmd)
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {clustered}'
    os.system(cmd)

    # output handling
    os.system(f'cp {clustered} {outputfile.format("processed")}')
    os.system(f'cp {selected} {outputfile.format("filtered-selected")}')
    #os.system('rm *temp*.csv')
