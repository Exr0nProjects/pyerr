# type:ignore

import tqdm
import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from operator import itemgetter # https://stackoverflow.com/a/52083390/10372825
from ErrorProp import ErroredValue as EV

from config import PRINT_PRECISION

CM_PER_INCH = 2.54
MAX_COUNTRATE = 3500
GOOD_ENOUGH = 1e-9
OFF_FACTOR = 10

def readdata(dataitem):
    meta, data, background = itemgetter('meta', 'data', 'background')(dataitem)
    background_rate = EV(background["counts"], background["counts"]**0.5)/background["seconds"]
    background_rate = background_rate / (1-(background_rate/MAX_COUNTRATE))


    # here is the actual data analysis
    corrected_data = pd.DataFrame.copy(data)
    corrected_data["counts"] = data.apply(lambda row: EV(row['counts'], row['counts']**0.5), axis=1)    # get std dev with sqrt
    corrected_data["cm"] = corrected_data.apply(lambda row: row["inches"]*CM_PER_INCH, axis=1)
    corrected_data["counts_sec"] = corrected_data.apply(lambda row: row["counts"]/row["seconds"], axis=1)

    corrected_data["deadtime_adjusted"] = corrected_data.apply(lambda row: (row["counts_sec"]/(1-(row['counts_sec']/MAX_COUNTRATE))), axis=1)
    corrected_data["true_counts_sec"] = corrected_data.apply(lambda row: row["deadtime_adjusted"]-background_rate, axis=1)

    unblocked_count = corrected_data.loc[corrected_data["inches"]==0]["true_counts_sec"][0]

    corrected_data["normalized_count_rate"] = corrected_data.apply(lambda row: row["true_counts_sec"]/unblocked_count, axis=1)

    halfthickness_predicted = corrected_data.iloc[1:].apply(lambda row: row["inches"]/(EV.ln(row["normalized_count_rate"])/math.log(0.5, math.e)), axis=1)

    corrected_data["predicted_halfthickness"] = pd.concat([pd.Series([EV(0)]), halfthickness_predicted]) # used custom log function for errors

    # renaming for convienence
    corrected_data.attrs["material"] = meta[0]
    corrected_data.attrs["source"] = meta[1]

    return corrected_data

def RelativeIntersity(T, tSeries):
    return tSeries.apply(lambda t: 0.5**(t/T))

def SSE(indicies, prediction, logits, logits_error, function):
    ri = function(prediction, indicies)
    return ((logits-ri)**2/logits_error**2).sum()

def unwrap(datatable):
    return datatable.inches, datatable.normalized_count_rate.apply(lambda x:x.value), datatable.normalized_count_rate.apply(lambda x:x.delta)

def sMinFit(function, param=1, lr=1e-7, delta=1e-8, epochs=int(1e6), ax=None):
    bar = tqdm.tqdm(range(epochs))

    incident = 0

    for it in bar:   # differentiable grad desc inspired by: https://towardsdatascience.com/implement-gradient-descent-in-python-9b93ed7108d1
        prev_p = param
        dydx = (function(param+delta) - function(param-delta))/(2*delta)
        param -= lr * dydx

        bar.set_description(f'param {param:.6f}, deriv {dydx:.6f}, change {abs(prev_p - param)}')

        newcost = function(param)
        oldcost = function(prev_p)

        # if something goes wrong (change faster than expected or loss increases)
        if abs(newcost-oldcost) > abs(OFF_FACTOR*dydx*(param-prev_p)) or newcost > oldcost:
            # half the learning rate and try again
            lr /= 2
            incident = it
            param = prev_p
            continue

        # no incidents in the past 1k steps, try converging faster
        if it - incident > 1e3:
            lr *= 1.2
            incident = it

        # updating slowly enough that we are probably converged
        if abs(prev_p - param) < GOOD_ENOUGH:
            break

    return param, function(param)

def calculateSfitUncert(bestx, besty, targety, function, ax=None, low=0, high=100):
    def bisect(low, high, target, function):
        if (low > high): low, high = high, low  # invariant: low is less equal to high
        while (high-low > GOOD_ENOUGH):
            mid = (low+high)/2
            if (function(mid) < target) == (function(low) < target):
                low = mid
            else:
                high = mid
        return low

    # binary search on min and max
    param_min = bisect(low, bestx, targety, function)
    param_max = bisect(bestx, high, targety, function)

    # plot everything
    if ax is not None:
        # plot neighborhood
        abs_err = max(bestx - param_min, param_max-bestx)

        # plot given information
        ax.axhline(y=besty, label=f"S min = {besty:.6f}", color='green')
        ax.axhline(y=targety, label=f"S min + chi^2 = {targety:.6f}", color='lightgreen')
        ax.axvline(x=bestx, label=f"T_best = {bestx:.6f}", color='green')

        # plot found information
        ax.axvline(x=param_min, label=f"T_min = {param_min:.6f}", color='red')
        ax.axvline(x=param_max, label=f"T_max = {param_max:.6f}", color='blue')

    return param_min, param_max

