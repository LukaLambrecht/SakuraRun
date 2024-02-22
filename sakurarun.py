##################################################
# Main script calculating the optimal sakura run #
##################################################


# local imports
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


if __name__=='__main__':

    # load input file (test file for now)
    inputfile = 'data/test.csv'
    df = pd.read_csv(inputfile, delimiter=';')

    # get coordinates in suitable format
    coords = df_to_coords(df)

    # make requests session
    session = requests.Session()

    # calculate distance matrix
    distances = get_distance_matrix(coords, session=session, profile='foot')
    plot_distance_matrix(coords, distances=distances)

    # optimization of route
    # to be done, dummy for now
    ids = list(range(len(coords)))

    # calculate route
    (route_coords, route_info) = get_route_coords(coords, session=session, profile='foot')
    
    # print some info and make plot
    print('Total distance: {} km'.format(route_info['distance']/1000))
    plot_route_coords(coords, route_coords=route_coords)

    # write output KML file (e.g. for use in google maps)
    kmlcontent = coords_to_kml(route_coords)
    kmlfile = 'test.kml'
    with open(kmlfile, 'w') as f:
        f.write(kmlcontent)
