import numpy as np
import python_tsp
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.heuristics import solve_tsp_local_search
from python_tsp.heuristics import solve_tsp_simulated_annealing


def solve_tsp(distances, method='exact'):
	# solve the traveling salesperson problem for a given distance matrix
	# input arguments:
	# - distances: square np array with distances
	# - method: choose from 'exact', 'local' or 'annealing'
	# returns:
	#   a tuple with the shortes path indices and distance
	if method=='exact':
	    shortest_path_inds, shortest_path_dist = solve_tsp_dynamic_programming(distances)
	elif method=='local':
	    shortest_path_inds, shortest_path_dist = solve_tsp_local_search(distances)
	elif method=='annealing':
	    shortest_path_inds, shortest_path_dist = solve_tsp_simulated_annealing(distances)
	else:
	    msg = 'Method "{}" not recognized.'.format(method)
	    raise Exception(msg)
	# add the first index to the end to make the closed loop explicit
	shortest_path_inds = shortest_path_inds + [shortest_path_inds[0]]
	return (shortest_path_inds, shortest_path_dist)
