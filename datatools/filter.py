#########################
# Filter input csv file #
#########################


import os
import sys
import json
import copy
import argparse
import pandas as pd


class Filter(object):

    def __init__(self):
        self.select = None
        self.veto = None
        self.properties = ['select', 'veto']

    def __str__(self):
        parts = ['Filter:']
        for p in self.properties:
            parts.append( f'  - {p}: {getattr(self, p)}' )
        return '\n'.join(parts)

    @classmethod
    def from_dict(cls, fdict):
        # todo: implement more extensive format checking
        f = Filter()
        keys = ['select', 'veto']
        for key in keys:
            if key in fdict.keys():
                setattr(f, key, copy.deepcopy(fdict[key]))
        for key in fdict.keys():
            if key not in keys:
                msg = f'WARNING: key {key} not recognized and will be ignored.'
                print(msg)
        return f

    @classmethod
    def from_json(cls, jsonfile):
        with open(jsonfile, 'r') as f:
            fdict = json.load(f)
        return cls.from_dict(fdict)

    def filter_df(self, df, key):
        res = df
        if self.select is not None: res = res[res[key].isin(self.select)]
        if self.veto is not None: res = res[~res[key].isin(self.veto)]
        return res


if __name__=='__main__':
   
    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--treetype_key', default=None)
    parser.add_argument('--print_treetypes', default=False, action='store_true')
    parser.add_argument('--treetype_filter', default=None)
    parser.add_argument('--location_key', default=None)
    parser.add_argument('--print_locations', default=False, action='store_true')
    parser.add_argument('--location_filter', default=None)
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # parse treetype filter
    treetype_filter = args.treetype_filter
    if args.treetype_filter is not None:
        args.treetype_filter = os.path.abspath(args.treetype_filter)
        if not os.path.exists(args.treetype_filter):
            raise Exception('treetype_filter {} does not exist.'.format(args.treetype_filter))
        treetype_filter = Filter.from_json(args.treetype_filter)
        print('Read treetype filter:')
        print(treetype_filter)

    # parse location filter
    location_filter = args.location_filter
    if args.location_filter is not None:
        args.location_filter = os.path.abspath(args.location_filter)
        if not os.path.exists(args.location_filter):
            raise Exception('location_filter {} does not exist.'.format(args.location_filter))
        location_filter = Filter.from_json(args.location_filter)
        print('Read location filter:')
        print(location_filter)

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    if args.treetype_key is not None:

        # print tree types
        treetypes = list(set(dataset[args.treetype_key]))
        treetypes = [el for el in treetypes if isinstance(el, str)]
        treetypes = sorted(treetypes)
        if args.print_treetypes:
            print('Available tree types:')
            for treetype in treetypes: print('  - {}'.format(treetype))
    
        # filter on tree type
        if treetype_filter is not None:
            dataset = treetype_filter.filter_df(dataset, args.treetype_key)
        print('Number of entries after tree type filter: {}'.format(len(dataset)))
    
    if args.location_key is not None:

        # print locations
        locations = list(set(dataset[args.location_key]))
        locations = [el for el in locations if isinstance(el, str)]
        locations = sorted(locations)
        if args.print_locations:
            print('Available locations:')
            for location in locations: print('  - {}'.format(location))
    
        # filter on location
        if location_filter is not None:
            dataset = location_filter.filter_df(dataset, args.location_key)
        print('Number of entries after location filter: {}'.format(len(dataset)))

    # write filtered dataset
    if args.outputfile is not None:
        dataset.to_csv(args.outputfile, sep=args.delimiter, index=False)
