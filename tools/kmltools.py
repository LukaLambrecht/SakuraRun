############################################
# Tools for reading and writing .kml files #
############################################


def coords_to_kml(coords, color=None):
    # convert a list of coordinates to kml format
    # input arguments:
    # - coords: list of coordinates formatted as {'lon': longitude, 'lat': latitude}
    # returns:
    #   content of a kml file in str format
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    header += '<kml xmlns="http://earth.google.com/kml/2.0"> <Document>\n'
    header += '<Placemark>\n'
    coords = ['{}, {}, 0.'.format(coord['lon'], coord['lat']) for coord in coords]
    coords = '\n'.join(coords)
    coords = '<LineString> <coordinates>\n' + coords + '\n' + '</coordinates> </LineString>\n'
    style = '<Style> <LineStyle>\n'
    if color is not None: style += '<color>{}</color>\n'.format(color)
    style += '</LineStyle> </Style>\n'
    footer = '</Placemark> </Document> </kml>'
    return header + coords + style + footer
