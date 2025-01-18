###############################################
# Parse the csv file to a conventional format #
###############################################


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
    parser.add_argument('--dtype', default='street', choices=['street', 'parks'])
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=',')
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    # rename columns
    rename = {
      'spp_bot': 'treetype',
      'y_latitude': 'lat',
      'x_longitude': 'lon'
    }
    if args.dtype=='street': rename['street'] = 'street'
    elif args.dtype=='parks': rename['park'] = 'street'
    dataset.rename(columns=rename, inplace=True)

    # remove unneeded columns
    keep = list(rename.values())
    drop = [c for c in dataset.columns if c not in keep]
    dataset.drop(columns=drop, inplace=True)

    # write to output file
    if args.outputfile is not None:
        dataset.to_csv(args.outputfile, sep=',')
