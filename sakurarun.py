##################################################
# Main script calculating the optimal sakura run #
##################################################


# local imports
import os
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
    parser.add_argument('-i', '--inputfile', type=os.path.abspath)
    parser.add_argument('-o', '--outputfile', default='sakurarun.kml', type=os.path.abspath)
    parser.add_argument('-p', '--profile', default='foot')
    parser.add_argument('-t', '--threshold', default=0.05, type=float)
    parser.add_argument('--delimiter', default=',')
    parser.add_argument('--pause', default=0, type=float)
    parser.add_argument('--doplot', default=False, action='store_true')
    args = parser.parse_args()

    # load input file
    df = pd.read_csv(args.inputfile, delimiter=args.delimiter)
    print('Read input file {} with {} entries.'.format(args.inputfile, len(df)))

    # get coordinates in suitable format
    coords = df_to_coords(df)

    # make requests session
    session = requests.Session()

    # calculate distance matrix
    print('Calculating distance matrix...')
    distances = get_distance_matrix(coords, session=session, profile=args.profile)
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

    # wait for minutely quota to replenish
    if args.pause>0:
        print('Waiting for {}s...'.format(args.pause))
        time.sleep(args.pause)

    # calculate route
    print('Calculating route details...')
    (route_coords, route_info) = get_route_coords(coords, session=session, profile=args.profile)
    
    # print some info and make plot
    print('Total distance: {:.3f} km'.format(route_info['distance']/1000))
    if args.doplot: plot_route_coords(coords, route_coords=route_coords)

    # write output KML file (e.g. for use in google maps)
    kmlcontent = coords_to_kml(route_coords)
    outputdir = os.path.dirname(args.outputfile)
    if not os.path.exists(outputdir): os.makedirs(outputdir)
    with open(args.outputfile, 'w') as f:
        f.write(kmlcontent)
