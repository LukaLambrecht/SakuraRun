###################################
# Tools for filtering a dataframe #
###################################


import os
import sys
import json
import copy
import argparse
import pandas as pd
from fnmatch import fnmatch


class Filter(object):

    def __init__(self, column_name=None, select=None, veto=None):
        self.column_name = column_name
        self.select = select
        self.veto = veto
        self.properties = ['column_name', 'select', 'veto']

    def __str__(self):
        parts = ['Filter:']
        for p in self.properties:
            parts.append( f'  - {p}: {getattr(self, p)}' )
        return '\n'.join(parts)

    @classmethod
    def from_dict(cls, fdict):
        # todo: implement more extensive format checking
        f = Filter()
        keys = ['column_name', 'select', 'veto']
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

    def filter_df(self, df):
        res = df.copy()
        if self.column_name is None:
            raise Exception('Cannot apply this filter as the column_name was not set.')
        if self.select is not None: res = res[res[self.column_name].isin(self.select)]
        if self.veto is not None: res = res[~res[self.column_name].isin(self.veto)]
        res.reset_index(inplace=True)
        return res
    
    
def filter_dataset(dataset, filters, verbose=False):
    # main function
    
    # parse filters
    for idx, dffilter in enumerate(filters):
        if isinstance(dffilter, Filter): pass
        elif isinstance(dffilter, str):
            dffilter = os.path.abspath(dffilter)
            if not os.path.exists(dffilter):
                raise Exception(f'Filter {dffilter} does not exist.')
            dffilter = Filter.from_json(dffilter)
            filters[idx] = dffilter
        if not isinstance(dffilter, Filter):
            raise Exception(f'Filter is of unrecognized type {type(dffilter)}.')

    # printout
    if verbose:
        print('Found following filters:')
        for dffilter in filters:
            print(dffilter)

    # do filtering
    for dffilter in filters:
        column_name = dffilter.column_name
        if verbose: print(f'Filtering {column_name}...')

        # print available values
        if verbose:
            values = list(set(dataset[column_name]))
            values = [el for el in values if isinstance(el, str)]
            values = sorted(values)
            print('Available values:')
            for value in values: print('  - {}'.format(value))
    
        # do filtering
        dataset = dffilter.filter_df(dataset)
        if verbose: print('Number of entries after this filter: {}'.format(len(dataset)))
    
    return dataset


if __name__=='__main__':
   
    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default=None)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--filters', default=None, nargs='+')
    args = parser.parse_args()
    print('Running with following configuration:')
    for arg in vars(args): print(f'  - {arg}: {getattr(args, arg)}')

    # load input file
    dataset = pd.read_csv(args.inputfile, sep=args.delimiter)
    print('Loaded dataset {}'.format(args.inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    print('Column names:')
    print(list(dataset.columns.values))

    # do filtering
    filtered_dataset = filter_dataset(
      dataset,
      filters = args.filters,
      verbose = True
    )

    # write filtered dataset
    if args.outputfile is not None:
        filtered_dataset.to_csv(args.outputfile, sep=args.delimiter, index=False)
