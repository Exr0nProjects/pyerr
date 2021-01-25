import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

from ErrorProp import ErroredValue

def get():
    return {    # peter tissue orange
        'name': ('tissues', 'orange'),
        'data': pd.dataframe(data={
            'inches': [ 0, 6, 12, 24],
            'seconds': [400]*4,
            'counts': [4358, 4116, 4041, 4052]}),
        'background': { 'seconds': 300, 'counts': 39 }
    };

if __name__ == '__main__':
    pass

