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
    inputfile = os.path.abspath(os.path.join(thisdir, 'raw/locaties-bomen-gent-full.csv'))
    outputfile = 'data-gent-{}.csv'
    treetype_key = 'sortiment'
    treetype_filter = os.path.abspath(os.path.join(thisdir, 'filters/treetype_filter.json'))
    location_key = 'onderhoudsgebied'
    location_filter = os.path.abspath(os.path.join(thisdir, 'filters/location_filter.json'))

    # filter
    filtered = 'temp-1.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'filter.py')
    cmd += f' -i {inputfile}'
    cmd += f' -o {filtered}'
    cmd += f' --treetype_key {treetype_key}'
    cmd += f' --treetype_filter {treetype_filter}'
    cmd += f' --location_key {location_key}'
    cmd += f' --location_filter {location_filter}'
    os.system(cmd)

    # parse
    parsed = 'temp-2.csv'
    cmd = 'python3 parse.py'
    cmd += f' -i {filtered}'
    cmd += f' -o {parsed}'
    os.system(cmd)

    # cluster
    clustered = 'temp-3.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'cluster_streets.py')
    cmd += f' -i {parsed}'
    cmd += f' -o {clustered}'
    os.system(cmd)

    # plotting
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {parsed}'
    os.system(cmd)
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {clustered}'
    os.system(cmd)

    # output handling
    os.system(f'cp {clustered} {outputfile.format("processed")}')
    os.system(f'cp {parsed} {outputfile.format("filtered")}')
    os.system('rm *temp*.csv')
