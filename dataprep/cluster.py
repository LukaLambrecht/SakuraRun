# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 20:36:02 2024

@author: Luka
"""

import os
import sys
import pandas as pd
import numpy as np

def average_geo_points(df):
	geo_points = df['geo_point_2d']
	lats = []
	lons = []
	for geo_point in geo_points:
		temp = geo_point.split(',')
		lat = float(temp[0])
		lon = float(temp[1])
		lats.append(lat)
		lons.append(lon)
	lat_avg = np.average(lats)
	lon_avg = np.average(lons)
	geo_point_avg = '{}, {}'.format(lat_avg, lon_avg)
	row = df.iloc[[0]].copy()
	row['geo_point_2d'] = geo_point_avg
	return row

if __name__=='__main__':
	
	# load input file
	inputfile = '../data/locaties-bomen-gent-filtered.csv'
	dataset = pd.read_csv(inputfile, sep=',')
	print('Loaded dataset {}'.format(inputfile))
	print('Number of entries: {}'.format(len(dataset)))
	#print('Dataset head:')
	#print(dataset.head())
	#print('Column names:')
	#print(dataset.columns)
	
	# split the data based on street name
	streets = sorted(list(set(dataset['straatnaam'])))
	datasets = []
	for street in streets:
		part = dataset[dataset['straatnaam']==street]
		datasets.append(part)
	print('Found {} clusters based on street name'.format(len(datasets)))
	
	# cluster each part
	cluster_centers = []
	for part in datasets:
		cluster = average_geo_points(part)
		cluster_centers.append(cluster)
		
	# combine cluster centers in a dataframe and save to output file
	cluster_centers = pd.concat(cluster_centers, ignore_index=True)
	outputfile = '../data/locaties-bomen-gent-filtered-clustered.csv'
	cluster_centers.to_csv(outputfile, sep=',')