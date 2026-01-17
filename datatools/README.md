# Tools for data parsing


### Introduction
Tools for converting data from whatever raw input format they are in,
to a conventional format that can be used as input to the route optimizer.

Input data are typically available in a `.csv` file or similar table-like structure,
that can be read into a `pandas.DataFrame`.

The tools in this folder manipulate the dataframe in order to bring it into a conventional format.
Among other things, these tools allow:
- filtering rows on specific values in specific columns.
- selection of certain simple geographical areas (squares and circles defined by coordinates).
- clustering of nearby entries into one, to reduce the size of the distance matrix.
- renaming columns and discarding superfluous columns.

Note: these are just tools; every specific input format will require its own dedicated parsing sequence.


### TreeDF

