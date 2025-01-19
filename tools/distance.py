import os
import sys
import math
import numpy as np


def haversine(lat1, lon1, lat2, lon2):
    # haversine formula
    r = 6371000 # (in meter)
    p = math.pi / 180.
    a = ( 0.5 - math.cos((lat2-lat1)*p)/2.
        + math.cos(lat1*p) * math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p))/2. )
    return 2 * r * math.asin(math.sqrt(a))
