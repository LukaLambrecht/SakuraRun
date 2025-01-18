#########################
# Filter input csv file #
#########################


import os
import sys
import argparse
import pandas as pd
from fnmatch import fnmatch


if __name__=='__main__':
   
    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--treetype_key', default=None)
    parser.add_argument('--match_pattern', default=None)
    parser.add_argument('--count', default=False, action='store_true')
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

    # get all tree types
    treetypes = list(set(dataset[args.treetype_key]))
    treetypes = [el for el in treetypes if isinstance(el, str)]
    treetypes = sorted(treetypes)

    # do filtering
    if args.match_pattern is not None:
        treetypes = [el for el in treetypes if fnmatch(el, args.match_pattern)]

    # do counting
    if args.count:
        ntrees = [ len(dataset[dataset[args.treetype_key] == el]) for el in treetypes ]

    # do printing
    msg = 'Available tree types'
    if args.match_pattern is not None:
        msg += f' (matching pattern {args.match_pattern})'
    msg += f' ({len(treetypes)}):'
    print(msg)
    for idx, treetype in enumerate(treetypes):
        msg = f'  - {treetype}'
        if args.count: msg += f' ({ntrees[idx]})'
        print(msg)
    if args.count: print(f'Total: {sum(ntrees)}')
