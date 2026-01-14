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
    inputfile = os.path.abspath(os.path.join(thisdir, 'raw/SIPV_ICA_ARBRE_ISOLE.csv'))
    outputfile = 'data-geneve-{}.csv'
    treetype_key = 'NOM_COMPLET'
    treetype_filter = os.path.abspath(os.path.join(thisdir, 'filters/treetype_filter.json'))

    # filter
    filtered = 'temp-1.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'filter.py')
    cmd += f' -i {inputfile}'
    cmd += f' -o {filtered}'
    cmd += ' --delimiter \';\''
    cmd += f' --treetype_key {treetype_key}'
    cmd += f' --treetype_filter {treetype_filter}'
    #cmd += f' --print_treetypes'
    os.system(cmd)

    # parse
    parsed = 'temp-2.csv'
    cmd = 'python3 parse.py'
    cmd += f' -i {filtered}'
    cmd += f' -o {parsed}'
    os.system(cmd)

    # limit area
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'select_square.py')
    cmd += f' -i {parsed}'
    cmd += f' -o {parsed}'
    cmd += ' --lat_min 46.195'
    cmd += ' --lat_max 46.22'
    cmd += ' --lon_min 6.125'
    cmd += ' --lon_max 6.18'
    os.system(cmd)

    # cluster
    clustered = 'temp-3.csv'
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'cluster_distance.py')
    cmd += f' -i {parsed}'
    cmd += f' -o {clustered}'
    cmd += f' --threshold_distance 100'
    os.system(cmd)

    # plotting
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {parsed}'
    os.system(cmd)
    cmd = 'python3 ' + os.path.join(datatoolsdir, 'plot_locations.py')
    cmd += f' -i {clustered}'
    cmd += f' --num_key num'
    os.system(cmd)

    # output handling
    os.system(f'cp {clustered} {outputfile.format("processed")}')
    os.system(f'cp {parsed} {outputfile.format("filtered")}')
    os.system('rm *temp*.csv')
