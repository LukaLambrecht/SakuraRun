#########################
# Filter input csv file #
#########################


import os
import sys
import pandas as pd


if __name__=='__main__':
    
    # load input file
    inputfile = '../data/locaties-bomen-gent-full.csv'
    dataset = pd.read_csv(inputfile, sep=';')
    print('Loaded dataset {}'.format(inputfile))
    print('Number of entries: {}'.format(len(dataset)))
    print('Dataset head:')
    print(dataset.head())
    print('Column names:')
    print(dataset.columns)
    
    # print tree types
    treetypes = list(set(dataset['sortiment']))
    treetypes = [el for el in treetypes if isinstance(el, str)]
    treetypes = sorted(treetypes)
    print('Available tree types:')
    for treetype in treetypes:
        if treetype.startswith('Prunus'): print('  - {}'.format(treetype))
    
    # filter on tree type
    treetypes = ([
        'Prunus serrulata',
        'Prunus serrulata \'Kanzan\'',
        'Prunus serrulata  \'Amonogawa\'',
        'Prunus serrulata \'Pendula\''
    ])
    dataset = dataset[dataset['sortiment'].isin(treetypes)]
    print('Number of entries after tree type filter: {}'.format(len(dataset)))
    
    # print locations
    locations = list(set(dataset['onderhoudsgebied']))
    locations = [el for el in locations if isinstance(el, str)]
    locations = sorted(locations)
    print('Available locations:')
    for location in locations:
        print('  - {}'.format(location))
        
    # filter on location
    veto = ([
        'Drongen',
        'Mariakerke',
        'New-Orleans',
        'Nieuw-Gent',
        'Oostakker',
        'Sint-Amandsberg',
        'Sint-Denijs-Westrem',
        'Wondelgem Dries',
        'Wondelgem Gavers'
    ])
    allowed_locations = [el for el in locations if el not in veto]
    dataset = dataset[dataset['onderhoudsgebied'].isin(allowed_locations)]
    print('Number of entries after location filter: {}'.format(len(dataset)))
    
    # write filtered dataset
    outputfile = '../data/locaties-bomen-gent-filtered.csv'
    dataset.to_csv(outputfile, sep=',')
