#####################################################
# Make a selection based on max and min lat and lon #
#####################################################


import os
import sys
import argparse
import pandas as pd


def select_square(dataset,
                  lat_key=None, lat_min=None, lat_max=None,
                  lon_key=None, lon_min=None, lon_max=None,
                  verbose=False):
    # main function
    if lat_key is None: lat_key = 'lat'
    if lon_key is None: lon_key = 'lon'
    norig = len(dataset)
    if lat_min is not None: dataset = dataset[dataset[lat_key] > float(lat_min)]
    if lat_max is not None: dataset = dataset[dataset[lat_key] < float(lat_max)]
    if lon_min is not None: dataset = dataset[dataset[lon_key] > float(lon_min)]
    if lon_max is not None: dataset = dataset[dataset[lon_key] < float(lon_max)]
    nafter = len(dataset)
    if verbose:
        print(f'INFO in select_square: selected {nafter} out of {norig} instances.')
    return dataset


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
    print('Column names:')
    print((dataset.columns.values))

    # do selections
    dataset = select_square(dataset,
                          lat_key=args.lat_key, lat_min=args.lat_min, lat_max=args.lat_max,
                          lon_key=args.lon_key, lon_min=args.lon_min, lon_max=args.lon_max)

    # do printout
    print('Selected {} entries'.format(len(dataset)))

    # write output file
    if args.outputfile is not None:
        dataset.to_csv(args.outputfile, sep=args.delimiter, index=False)
