##################################################
# Main script calculating the optimal sakura run #
##################################################


# local imports
import os
import sys
import numpy as np
import pandas as pd
import requests
import argparse
# import GraphHopper API key
from api.api_key import API_KEY
# local imports
from distancematrix import get_distance_matrix
from distancematrix import plot_distance_matrix
from route import get_route_coords
from route import plot_route_coords
from tools.coordtools import df_to_coords
from tools.kmltools import coords_to_kml
from tools.tsptools import solve_tsp


if __name__=='__main__':

    # read command line arguments
    parser = argparse.ArgumentParser(description='Calculate optimal sakura run')
    parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
            help='Input .csv file with cluster locations.')
    parser.add_argument('-o', '--outputfile', default='sakurarun.kml', type=os.path.abspath,
            help='Output .kml file with route markers (default: "sakurarun.kml").')
    parser.add_argument('-p', '--profile', default='foot',
            help='Transportation profile (default: "foot").')
    parser.add_argument('-t', '--threshold', default=0.05, type=float,
            help='Relative difference threshold for method cross-checking (default: 0.05).')
    parser.add_argument('--delimiter', default=',',
            help='Delimiter for reading .csv file (default: ",")')
    parser.add_argument('--blocksize', default=None,
            help='Block size for distance matrix calculation, must be None'
                +' or an integer between 2 and the number of points in the input file;'
                +' use a value <= 5 for compatibility with a free GraphHopper account.')
    parser.add_argument('--chunksize', default=None,
            help='Chunk size for route calculation, must be None'
                +' or an integer between 2 and the number of points in the input file;'
                +' use a value <= 5 for compatibility with a free GraphHopper account.')
    parser.add_argument('--doplot', default=False, action='store_true',
            help='Make plots of distance matrix and final optimal route.')
    args = parser.parse_args()

    # format blocksize argument
    if args.blocksize is not None: args.blocksize = int(args.blocksize)

    # format chunksize argument
    if args.chunksize is not None: args.chunksize = int(args.chunksize)

    # load input file
    df = pd.read_csv(args.inputfile, delimiter=args.delimiter)
    print('Read input file {} with {} entries.'.format(args.inputfile, len(df)))

    # get coordinates in suitable format
    coords = df_to_coords(df)

    # make requests session
    session = requests.Session()

    # calculate distance matrix
    print('Calculating distance matrix...')
    distances = get_distance_matrix(coords,
            session=session, profile=args.profile, blocksize=args.blocksize)
    if args.doplot: plot_distance_matrix(coords, distances=distances)

    # optimization of route
    print('Finding shortest path...')
    (ids, dist) = solve_tsp(distances, method='local')
    coords = [coords[idx] for idx in ids]
    print('Shortest path: {:.3f} km'.format(dist/1000))

    # cross-check with other heuristic methods
    check_methods = ['annealing']
    if args.threshold > 0:
        print('Cross-checking result...')
        for method in check_methods:
            (_, check_dist) = solve_tsp(distances, method=method)
            if np.abs(dist-check_dist)/dist > args.threshold:
                msg = 'WARNING: found more than {}% deviation'.format(args.threshold*100)
                msg += ' in cross-check with method "{}"'.format(method)
                print(msg)

    # calculate route
    print('Calculating route details...')
    (route_coords, route_info) = get_route_coords(coords,
            session=session, profile=args.profile, chunksize=args.chunksize)
    
    # print some info and make plot
    print('Total distance: {:.3f} km'.format(route_info['distance']/1000))
    if args.doplot: plot_route_coords(coords, route_coords=route_coords)

    # write output KML file (e.g. for use in google maps)
    kmlcontent = coords_to_kml(route_coords)
    outputdir = os.path.dirname(args.outputfile)
    if not os.path.exists(outputdir): os.makedirs(outputdir)
    with open(args.outputfile, 'w') as f:
        f.write(kmlcontent)
