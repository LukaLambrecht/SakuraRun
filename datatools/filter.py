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
    
    
def filter_dataset(dataset,
           treetype_key=None, print_treetypes=False, treetype_filter=None,
           location_key=None, print_locations=False, location_filter=None):
    # main function
    
    # parse treetype filter
    if treetype_filter is not None:
        if isinstance(treetype_filter, str):
            treetype_filter = os.path.abspath(treetype_filter)
            if not os.path.exists(treetype_filter):
                raise Exception('treetype_filter {} does not exist.'.format(treetype_filter))
            treetype_filter = Filter.from_json(treetype_filter)
        if not isinstance(treetype_filter, Filter):
            raise Exception('treetype_filter is of unrecognized type {}.'.format(treetype_filter))
        print('Read treetype filter:')
        print(treetype_filter)

    # parse location filter
    if location_filter is not None:
        if isinstance(location_filter, str):
            location_filter = os.path.abspath(location_filter)
            if not os.path.exists(location_filter):
                raise Exception('location_filter {} does not exist.'.format(location_filter))
            location_filter = Filter.from_json(location_filter)
        if not isinstance(location_filter, Filter):
            raise Exception('location_filter is of unrecognized type {}.'.format(location_filter))
        print('Read location filter:')
        print(location_filter)
        
    if treetype_key is not None:

        # print tree types
        treetypes = list(set(dataset[treetype_key]))
        treetypes = [el for el in treetypes if isinstance(el, str)]
        treetypes = sorted(treetypes)
        if print_treetypes:
            print('Available tree types:')
            for treetype in treetypes: print('  - {}'.format(treetype))
    
        # filter on tree type
        if treetype_filter is not None:
            print('Performing filtering based on tree type...')
            dataset = treetype_filter.filter_df(dataset, treetype_key)
            print('Number of entries after tree type filter: {}'.format(len(dataset)))
    
    if location_key is not None:

        # print locations
        locations = list(set(dataset[location_key]))
        locations = [el for el in locations if isinstance(el, str)]
        locations = sorted(locations)
        if print_locations:
            print('Available locations:')
            for location in locations: print('  - {}'.format(location))
    
        # filter on location
        if location_filter is not None:
            print('Performing filtering based on location...')
            dataset = location_filter.filter_df(dataset, location_key)
            print('Number of entries after location filter: {}'.format(len(dataset)))
            
    return dataset


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

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    #print('Dataset head:')
    #print(dataset.head())
    print('Column names:')
    print(dataset.columns)

    # do filtering
    filtered_dataset = filter_dataset(dataset,
      treetype_key=args.treetype_key, print_treetypes=args.print_treetypes, treetype_filter=args.treetype_filter,
      location_key=args.location_key, print_locations=args.print_locations, location_filter=args.location_filter)

    # write filtered dataset
    if args.outputfile is not None:
        filtered_dataset.to_csv(args.outputfile, sep=args.delimiter, index=False)
