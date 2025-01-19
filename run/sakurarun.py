#!/usr/bin/env python3

##################################################
# Main script calculating the optimal sakura run #
##################################################


# external imports
import os
import sys
import numpy as np
import pandas as pd
import requests
import argparse

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(thisdir, '..')))

# import GraphHopper API key
from api.api_key import API_KEY

# local imports
from python.distancematrix import get_distance_matrix
from python.distancematrix import plot_distance_matrix
from python.route import get_route_coords
from python.route import plot_route_coords
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
    parser.add_argument('--lat_key', default='lat',
            help='Name of the column with latitude values in input .csv file (default: "lat").')
    parser.add_argument('--lon_key', default='lon',
            help='Name of the column with longitude values in input .csv file (default: "lon").')
    parser.add_argument('--blocksize', default=None,
            help='Block size for distance matrix calculation, must be None'
                +' or an integer between 2 and the number of points in the input file;'
                +' use a value <= 5 for compatibility with a free GraphHopper account.')
    parser.add_argument('--plot_distance_matrix', default=False, action='store_true',
            help='Make plot of distance matrix.')
    parser.add_argument('--geodesic_distance_matrix', default=False, action='store_true',
            help='Use a simple geodesic distance matrix instead of a fully accurate one.')
    parser.add_argument('--kmeans_distance_matrix', default=False, action='store_true',
            help='Use k-means clustering before distance matrix computation.')
    parser.add_argument('--plot_tsp', default=False, action='store_true',
            help='Make plot shortest route solution.')
    parser.add_argument('--chunksize', default=None,
            help='Chunk size for route calculation, must be None'
                +' or an integer between 2 and the number of points in the input file;'
                +' use a value <= 5 for compatibility with a free GraphHopper account.')
    parser.add_argument('--plot_route', default=False, action='store_true',
            help='Make plot of final optimal route.')
    args = parser.parse_args()

    # format blocksize argument
    if args.blocksize is not None: args.blocksize = int(args.blocksize)

    # format chunksize argument
    if args.chunksize is not None: args.chunksize = int(args.chunksize)

    # load input file
    df = pd.read_csv(args.inputfile, delimiter=args.delimiter)
    print('Read input file {} with {} entries.'.format(args.inputfile, len(df)))

    # get coordinates in suitable format
    lats = df[args.lat_key].astype(float)
    lons = df[args.lon_key].astype(float)
    coords = [{'lon': lon, 'lat': lat} for lon, lat in zip(lons, lats)]

    # make requests session
    session = requests.Session()

    # calculate distance matrix
    print('Calculating distance matrix...')
    sys.stdout.flush()
    distances = get_distance_matrix(coords,
            session=session, profile=args.profile, blocksize=args.blocksize,
            geodesic=args.geodesic_distance_matrix,
            kmeans=args.kmeans_distance_matrix)

    # plot distance matrix
    if args.plot_distance_matrix:
        print('Plotting distance matrix...')
        sys.stdout.flush()
        plot_distance_matrix(coords, distances=distances)

    # optimization of route
    print('Finding shortest path...')
    sys.stdout.flush()
    (ids, dist) = solve_tsp(distances, method='local')
    print('Shortest path: {:.3f} km'.format(dist/1000))
    sys.stdout.flush()

    # re-index coords and distances
    coords = [coords[idx] for idx in ids]
    new_distances = np.copy(distances)
    for i in range(distances.shape[0]):
        for j in range(distances.shape[1]):
            new_distances[i,j] = distances[ids[i], ids[j]]
    distances = new_distances

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

    # plot shortest route solution
    if args.plot_tsp:
        print('Plotting shortest route solution...')
        plot_distance_matrix(coords, distances=distances, mode='route')

    # calculate route
    print('Calculating route details...')
    (route_coords, route_info) = get_route_coords(coords,
            session=session, profile=args.profile, chunksize=args.chunksize)
    
    # print some info and make plot
    print('Total distance: {:.3f} km'.format(route_info['distance']/1000))
    if args.plot_route: plot_route_coords(coords, route_coords=route_coords)

    # write output KML file (e.g. for use in google maps)
    kmlcontent = coords_to_kml(route_coords)
    outputdir = os.path.dirname(args.outputfile)
    if not os.path.exists(outputdir): os.makedirs(outputdir)
    with open(args.outputfile, 'w') as f:
        f.write(kmlcontent)
