##################################################
# Main script calculating the optimal sakura run #
##################################################


# local imports
import numpy as np
import pandas as pd
import requests
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

    # load input file (test file for now)
    inputfile = 'data/test.csv'
    df = pd.read_csv(inputfile, delimiter=';')
    print('Read input file {} with {} entries.'.format(inputfile, len(df)))

    # get coordinates in suitable format
    coords = df_to_coords(df)

    # make requests session
    session = requests.Session()

    # calculate distance matrix
    print('Calculating distance matrix...')
    distances = get_distance_matrix(coords, session=session, profile='foot')
    plot_distance_matrix(coords, distances=distances)

    # optimization of route
    print('Finding shortest path...')
    (ids, dist) = solve_tsp(distances, method='local')
    coords = [coords[idx] for idx in ids]
    print('Shortest path: {:.3f} km'.format(dist/1000))
	
	# cross-check with other heuristic methods
    check_methods = ['annealing']
    threshold = 0.05
    print('Cross-checking result...')
    for method in check_methods:
	    (_, check_dist) = solve_tsp(distances, method=method)
	    if np.abs(dist-check_dist)/dist > threshold:
		    msg = 'WARNING: found more than {}% deviation in cross-check.'.format(threshold*100)
		    print(msg)

    # calculate route
    (route_coords, route_info) = get_route_coords(coords, session=session, profile='foot')
    
    # print some info and make plot
    print('Total distance: {:.3f} km'.format(route_info['distance']/1000))
    plot_route_coords(coords, route_coords=route_coords)

    # write output KML file (e.g. for use in google maps)
    kmlcontent = coords_to_kml(route_coords)
    kmlfile = 'test.kml'
    with open(kmlfile, 'w') as f:
        f.write(kmlcontent)
