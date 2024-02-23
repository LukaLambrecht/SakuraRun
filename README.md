# Calculate the optimal path for a sakura appreciation run

The blossoming of the Japanese cherry flower (Jap. sakura, Lat. Prunus serrulata) is quite a sight to behold.
In fact, it is so beautiful that we wanted to see *all* of them. 
And though we're always in for a good run, there's *many* cherry trees in and around the city of Ghent... 
So how do we go about this? SakuraRun to the rescue!

### Input data, filtering, and clustering
The project starts from the database holding the location, type, etc. of all trees in and around the city of Ghent, summing to a total of about 64k entries.
We select the species of *Prunus serrulata*, and filter out some of the more remote locations in the outskirts of the city.
The remaining number of entries is about 240, still too large for calculating a realistic distance matrix and applying a shortest-path algorithm.
Hence we cluster the trees in the same street into a single entry, reducing their number to only 30.

### Calculating the distance matrix
Solving the shortest-path problem involves calculating the distance between each pair of points.
In order to get realistic distance estimates, we use the Matrix API from GraphHopper.

### Calculating the shortest path
The shortest path is calculated using the `python\_tsp` package.
As an exact solution for this problem is intractable even for a very small number of points, several heuristics are used and compared against each other to check the solution.

### Calculating the details of the route
Once the optimal visiting order of the clusters has been determined, route details are calculated using the Routing API from GraphHopper. The result is 33.229 km... Perhaps some more filtering is required...

### Integration into Google MyMaps
The `csv` files holding the filtered and clustered trees, and the final route in the form of a `kml` file, can be uploaded in Google MyMaps to create an interactive view of the route.
