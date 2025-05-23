# Data and processing sequence for Providence (RI, USA)

### Raw data
The raw data can be retrieved from the [Providence Tree Inventory](https://data.providenceri.gov/Neighborhoods/Providence-Tree-Inventory/uv9w-h8i4/about_data).

### Data processing
The raw dataset contains 24,525 entries.  
After filtering on *Prunus serrulata* (including subtypes): 475 items remaining
(of which 36 do not have latitude / longitude coordinates added - ignore these for now).

<img src="docs/filtered.png">

After selecting only north-east section (College Hill): 166 items remaining.  
After clustering by street name: 76 items remaining.  
However, because of some very long streets,
and also because of some mislabeled data entries,
the centers of these 76 clusters are not always meaningful.
The clusters are therefore split by the criterion that the maximum intra-cluster distance is 100m.
This results 118 clusters.

<img src="docs/clustered.png">

### Shortest path calculation
The number of clustered items (118) is still too large for a full distance matrix calculation.
Instead, the geodesic approximation ('as the crow flies') is used, employing the haversine formula.
The shortest path according to this approximation is shown below.

<img src="docs/shortest_path_geodesic.png">

The detailed route corresponding to this trajectory is shown below. Its total distance is 31.582 km.

<img src="docs/optimal_route.png">

An interactive map of this route can be found [here](https://www.google.com/maps/d/u/0/edit?mid=1rFmKRlpUEEuuJFzEooowr8raS5VHxHA&usp=sharing).
This includes also a shorter southern loop of 16.598 km,
passing by a still respectable 88 cherry blossom trees.
