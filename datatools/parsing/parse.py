#########################################################
# Tools for renaming columns and similar simple parsing #
#########################################################


def parse(dataset, lat_column=None, lon_column=None, rename=None, extra_columns=None):

    # parse rename dict
    if rename is None: rename = {}
    if lat_column is not None: rename[lat_column] = 'lat'
    if lon_column is not None: rename[lon_column] = 'lon'

    # do renaming
    dataset.rename(columns=rename, inplace=True)

    # remove unneeded columns
    keep = list(rename.values()) + ['lat', 'lon']
    if extra_columns is not None: keep += extra_column
    drop = [c for c in dataset.columns.values if c not in keep]
    dataset.drop(columns=drop, inplace=True)

    return dataset
