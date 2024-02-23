######################################################
# Test consistency between distance matrix and route #
######################################################


import os
import sys
import requests
sys.path.append('..')
import route
import distancematrix as dm


if __name__=='__main__':
    # testing section

    # define settings
    profile = 'car'

    # define points
    p1 = {'lat': 51.048903, 'lon': 3.695139}
    p2 = {'lat': 51.046213, 'lon': 3.698381}
    p3 = {'lat': 51.052116, 'lon': 3.699504}
    coords = [p1, p2]

    # make requests session
    session = requests.Session()

    # get distance from distance matrix
    distances = dm.get_distance_matrix(coords, session=session, profile=profile)
    print(distances)

    # get distance from route
    route_coords, route_info = route.get_route_coords(coords, session=session, profile=profile)
    print(route_info)

    # plots
    dm.plot_distance_matrix(coords, distances=distances)
    route.plot_route_coords(coords, route_coords=route_coords)
