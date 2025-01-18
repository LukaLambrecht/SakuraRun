#####################################################
# Make a selection based on max and min lat and lon #
#####################################################


import os
import sys
import argparse
import pandas as pd
import numpy as np


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--lat_key', default='lat')
    parser.add_argument('--lat_min', default=None)
    parser.add_argument('--lat_max', default=None)
    parser.add_argument('--lon_key', default='lon')
    parser.add_argument('--lon_min', default=None)
    parser.add_argument('--lon_max', default=None)
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    # do selections
    if args.lat_min is not None: dataset = dataset[dataset[args.lat_key] > float(args.lat_min)]
    if args.lat_max is not None: dataset = dataset[dataset[args.lat_key] < float(args.lat_max)]
    if args.lon_min is not None: dataset = dataset[dataset[args.lon_key] > float(args.lon_min)]
    if args.lon_max is not None: dataset = dataset[dataset[args.lon_key] < float(args.lon_max)]

    # do printout
    print('Selected {} entries'.format(len(dataset)))

    # write output file
    if args.outputfile is not None:
        dataset.to_csv(args.outputfile, sep=args.delimiter)
