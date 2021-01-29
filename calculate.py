# type:ignore

import tqdm
import math
import pandas as pd
import numpy as np
from operator import itemgetter # https://stackoverflow.com/a/52083390/10372825
from ErrorProp import ErroredValue as EV

from config import PRINT_PRECISION

CM_PER_INCH = 2.54
MAX_COUNTRATE = 3500
GOOD_ENOUGH = 1e-9

def process(dataitem):
    meta, data, background = itemgetter('meta', 'data', 'background')(dataitem)
    background_rate = EV(background["counts"], background["counts"]**0.5)/background["seconds"]
    background_rate = background_rate / (1-(background_rate/MAX_COUNTRATE))


    # get std dev with sqrt
    corrected_data = pd.DataFrame.copy(data)
    corrected_data["counts"] = data.apply(lambda row: EV(row['counts'], row['counts']**0.5), axis=1)
    corrected_data["cm"] = corrected_data.apply(lambda row: row["inches"]*CM_PER_INCH, axis=1)
    corrected_data["counts_sec"] = corrected_data.apply(lambda row: row["counts"]/row["seconds"], axis=1)

    corrected_data["deadtime_adjusted"] = corrected_data.apply(lambda row: (row["counts_sec"]/(1-(row['counts_sec']/MAX_COUNTRATE))), axis=1)
    corrected_data["true_counts_sec"] = corrected_data.apply(lambda row: row["deadtime_adjusted"]-background_rate, axis=1)
    # corrected_data["true_counts_sec"] = corrected_data.apply(lambda row: (row["counts_sec"]/(1-(row['counts_sec']/MAX_COUNTRATE)))-background_rate, axis=1)

    unblocked_count = corrected_data.loc[corrected_data["inches"]==0]["true_counts_sec"][0]

    corrected_data["normalized_count_rate"] = corrected_data.apply(lambda row: row["true_counts_sec"]/unblocked_count, axis=1)

    halfthickness_predicted = corrected_data.iloc[1:].apply(lambda row: row["inches"]/(EV.ln(row["normalized_count_rate"])/math.log(0.5, math.e)), axis=1)

    corrected_data["predicted_halfthickness"] = pd.concat([pd.Series([EV(0)]), halfthickness_predicted]) # used custom log function for errors

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

def sMinFit(datatable, function, param=1, lr=1e-4, epsilon=1e-8, epochs=100000):
    inches, logits, logits_err = unwrap(datatable)
    dydx = epsilon

    dydx = epsilon
    bar = tqdm.tqdm(range(epochs))

    for _ in bar:
        param_next = param-(dydx*lr+epsilon)
        loss = SSE(inches, param+epsilon, logits, logits_err, function)
        dydx = (loss-SSE(inches, param_next, logits, logits_err, function))/(param-param_next)
        param = param_next

        bar.set_description(f'Current fit: {param:2f}, Update: {dydx:2f}, Loss: {loss:2f}')

    return param, SSE(inches, param+epsilon, logits, logits_err, function)

    # breakpoint()

    # for _ in range(epochs):
    #     dydx = (SSE(inches, param, logits, logits_err, function)-SSE(inches, param-epsilon, logits, logits_err, function))/epsilon
    #     breakpoint()
    #     print(dydx)
    #     # weight update

def calculateSfitUncert(bestx, besty, targety, function, ax=None, low=0, high=100):
    def bisect(low, high, target, function):
        triedx, triedy = [], []
        if (low > high): low, high = high, low
        while (high-low > GOOD_ENOUGH):
            mid = (low+high)/2
            triedx.append(mid)
            triedy.append(function(mid))
            if (function(mid) < target) == (function(low) < target):
                low = mid
            else:
                high = mid
        return low, (triedx, triedy)

    # binary search on min and max
    param_min, tries_min = bisect(low, bestx, targety, function)
    param_max, tries_max = bisect(bestx, high, targety, function)

    # plot everything
    if ax is not None:
        # plot neighborhood
        abs_err = max(bestx - param_min, param_max-bestx)
        neighborhood = np.arange(bestx-abs_err*2, bestx+abs_err*2, abs_err*4/200)   # 200 evenly spaced points
        ax.scatter(neighborhood, list(map(function, neighborhood)), color='black', label='S(T)')

        # # plot binary search tries
        # ax.scatter(*tries_min, color='grey')
        # ax.scatter(*tries_max, color='grey')

        # plot given information
        ax.axhline(y=besty, label=f"S min = {besty:.6f}", color='green')
        ax.axhline(y=targety, label=f"S min + chi^2 = {targety:.6f}", color='lightgreen')
        ax.axvline(x=bestx, label=f"T_best = {bestx:.6f}", color='green')

        # plot found information
        ax.axvline(x=param_min, label=f"T_min = {param_min:.6f}", color='red')
        ax.axvline(x=param_max, label=f"T_min = {param_max:.6f}", color='blue')

    return param_min, param_max
