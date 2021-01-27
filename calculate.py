# type:ignore

import math
import pandas as pd
import numpy as np
from operator import itemgetter # https://stackoverflow.com/a/52083390/10372825
from ErrorProp import ErroredValue as EV

import matplotlib.pyplot as plt

CM_PER_INCH = 2.54
MAX_COUNTRATE = 3500

def process(dataitem):
    meta, data, background = itemgetter('meta', 'data', 'background')(dataitem)
    background_rate = EV(background["counts"], background["counts"]**0.5)/background["seconds"]

    # get std dev with sqrt
    corrected_data = pd.DataFrame.copy(data)
    corrected_data["counts"] = data.apply(lambda row: EV(row['counts'], row['counts']**0.5), axis=1)
    corrected_data["cm"] = corrected_data.apply(lambda row: row["inches"]*CM_PER_INCH, axis=1)
    corrected_data["counts_sec"] = corrected_data.apply(lambda row: row["counts"]/row["seconds"], axis=1)
    corrected_data["true_counts_sec"] = corrected_data.apply(lambda row: (row["counts_sec"]/(1-(row['counts_sec']/MAX_COUNTRATE)))-background_rate, axis=1)

    unblocked_count = corrected_data.loc[corrected_data["inches"]==0]["true_counts_sec"][0]

    corrected_data["normalized_count_rate"] = corrected_data.apply(lambda row: row["true_counts_sec"]/unblocked_count, axis=1)

    corrected_data.attrs["material"] = meta[0]
    corrected_data.attrs["source"] = meta[1]

    return corrected_data


