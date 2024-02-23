######################################
# Basic tests of route functionality #
######################################


import os
import sys
import requests
sys.path.append('..')
import route


if __name__=='__main__':
    # testing section

    # define points
    p1 = {'lat': 51.048903, 'lon': 3.695139}
    p2 = {'lat': 51.046213, 'lon': 3.698381}
    p3 = {'lat': 51.052116, 'lon': 3.699504}
    coords = [p2, p1, p3]

    # make requests session
    session = requests.Session()

    # get route
    route_coords = route.get_route_coords(coords, session=session)[0]

    # plot route
    route.plot_route_coords(coords, route_coords=route_coords)
