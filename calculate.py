# type:ignore

import tqdm
import math
import pandas as pd
import numpy as np
from operator import itemgetter # https://stackoverflow.com/a/52083390/10372825
from ErrorProp import ErroredValue as EV


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

def sMinFit(datatable, function, param=1, lr=1e-4, epsilon=1e-8, epochs=10000):
    logits = datatable.normalized_count_rate.apply(lambda x:x.value)
    logits_err = datatable.normalized_count_rate.apply(lambda x:x.delta)
    inches  = datatable.inches
    dydx = epsilon

    dydx = epsilon
    bar = tqdm.tqdm(range(epochs))

    minParam = param
    minS = int(1e10)

    for _ in bar:
        param_next = param-(dydx*lr+epsilon)
        loss = SSE(inches, param+epsilon, logits, logits_err, function)
        dydx = (loss-SSE(inches, param_next, logits, logits_err, function))/(param-param_next)
        param = param_next

        bar.set_description(f'Current fit: {param:2f}, Best fit: {minParam:2f}, Best loss: {minS:2f}')

        if loss < minS and param > 0:
            minParam = param
            minS = loss

    return minParam, minS

