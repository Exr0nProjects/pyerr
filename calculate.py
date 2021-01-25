import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

from ErrorProp import ErroredValue as EV

CM_PER_INCH = 2.54
FILEPATH = None     # TODO JACK
MAX_COUNTRATE = 3500

def get():
    return {    # peter tissue orange
        'meta': ('tissues', 'orange'),
        'data': pd.DataFrame(data={
            'inches': [ 0, 6, 12, 24],
            'seconds': [400]*4,
            'counts': [4358, 4116, 4041, 4052]}),
        'background': { 'seconds': 300, 'counts': 39 }
    };

if __name__ == '__main__':
    from operator import itemgetter # https://stackoverflow.com/a/52083390/10372825
    meta, data, background = itemgetter('meta', 'data', 'background')(get())
    # get std dev with sqrt
    with_errors = data.apply(lambda row: {
        'cm':      row['inches']*CM_PER_INCH,
        'seconds': row['seconds'],
        'counts':  EV(row['counts'], row['counts']**0.5)
    }, axis=1)

    print(type(with_errors))

    deadtime_corrected = with_errors.apply(lambda row: {
        'cm': row['cm'],
        'seconds': row['seconds'],
        'counts': row['counts']/(1-(row['counts']/MAX_COUNTRATE))
    }, axis=1)

    print(deadtime_corrected)


