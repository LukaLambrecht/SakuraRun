# Tools for clustering instances in a dataframe

Intended to reduce the dimension of the distance matrix to be calculated
(and hence the calculation time),
by grouping similar instances into one.

"Similar" instances can be defined based on mutual distance,
or based on categorical similarity based on the values of specified columns
(e.g. same street name).

The functions in this folder typically run on pandas dataframes with minimal assumptions,
except the presence of a column with latitude values, and a column with longitude values.
