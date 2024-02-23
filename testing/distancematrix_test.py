################################################
# Basic tests of distance matrix functionality #
################################################


import os
import sys
import requests
sys.path.append('..')
import distancematrix as dm


if __name__=='__main__':
    # testing section

    # define points
    p1 = {'lat': 51.048903, 'lon': 3.695139}
    p2 = {'lat': 51.046213, 'lon': 3.698381}
    p3 = {'lat': 51.052116, 'lon': 3.699504}
    coords = [p1,p2,p3]

    # make requests session
    session = requests.Session()

    # get distances
    distances = dm.get_distance_matrix(coords, session=session)
    print(distances)

    # plot distances
    dm.plot_distance_matrix(coords, distances=distances)
