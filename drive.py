# type:ignore

from ErrorProp import ErroredValue as EV

from datacleaning import globit
from multiprocessing import Pool
from Statistics import sMinFit, calculateSfitUncert, SSE
import math
from matplotlib import pyplot as plt
from operator import itemgetter # https://stackoverflow.com/a/52083390/10372825

from config import PRINT_PRECISION

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sys import argv


CM_PER_INCH = 2.54
MAX_COUNTRATE = 3500

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

def unwrap(datatable):
    return datatable.inches, datatable.normalized_count_rate.apply(lambda x:x.value), datatable.normalized_count_rate.apply(lambda x:x.delta)

def plot(index, ax=None):
    inches = results[index].inches
    ncr =  results[index].apply(lambda row:row["normalized_count_rate"].value, axis=1)
    delta =  results[index].apply(lambda row:row["normalized_count_rate"].delta, axis=1)

    inches, ncr, delta = zip(*sorted(zip(inches, ncr, delta)))

    ax.errorbar(inches, ncr, yerr=delta, color='#245b72', ecolor='#9ad2ea', elinewidth=1, label='NCR')
    ax.fill_between(np.array(inches), np.array(ncr)+np.array(delta), np.array(ncr)-np.array(delta), alpha=0.1)

    attrs = results[i].attrs
    ax.set_title(f"Thickness vs. NCR+Fit ({attrs['material']}, {attrs['source']})")
    ax.set_xlabel(f"Thickness ({'tissues' if 'tissue' in attrs['material'] else 'inches'})")
    ax.set_ylabel("Normalized Count Rate (cts/s)")
    ax.legend()


# breakpoint()
# Fitting Values with Inches
# ins,outs = sMinFit(results[1], RelativeIntersity, lr = 5e-10)
# Fitting values with # of Tissues
# ins,outs = sMinFit(results[4], RelativeIntersity, lr = 5e-8)

# for indx, result in enumerate(results):
# <<<<<<< HEAD

# print(len(results))

# _, indx = argv
# indx = int(indx)
# result = results[indx]
# t, smin = sMinFit(result, RelativeIntersity, lr = 2e-10, epochs=int(2e9))

# sMins.append(smin)
# fitTs.append(t)

# with open(f"out/result_{indx}.bin", "wb") as wb:
#     pickle.dump({"sMins": sMins, "fitTs": fitTs, "results":results}, wb)
# //=======
# //sMinFit(results[7], RelativeIntersity)
# //>>>>>>> Stashed changes

# breakpoint()
# =======
    # print(result.attrs["material"], result.predicted_halfthickness.apply(lambda row:row.value).mean())

def process(indx, ax=None, ax_alt=None):
    attrs = results[indx].attrs

    print(f"processsing {attrs['material']} {attrs['source']}")

    inches, logits, logits_err = unwrap(results[indx])
    cost_func = lambda T: SSE(RelativeIntersity, inches, T, logits, logits_err)

    t, smin = sMinFit(cost_func, lr = 5e-4 if "tissue" == attrs['material'] else 2e-7)

    t_min, t_max = calculateSfitUncert(t, smin, smin+1, cost_func, ax=ax_alt, low=1e-9, high=1e3*t)
    t_min, t_max = calculateSfitUncert(t, smin, smin+1, cost_func, ax=ax, low=1e-9, high=1e3*t)

    if ax is not None:
        neighborhood = np.arange(t-(t-t_min)*2, t+(t_max-t)*2, (t_max-t_min)*2/200)   # 200 evenly spaced points
        ax.scatter(neighborhood, list(map(cost_func, neighborhood)), color='black', label='S(T)')

        ax.set_title(f"Half-Thickness Fit ({attrs['material']}, {attrs['source']})")
        ax.set_xlabel(f"Half-Thickness T ({'tissues' if 'tissue' in results[indx].attrs['material'] else 'inches'})")
        ax.set_ylabel("S(T) (sum squared error)")
        ax.legend()

    if ax_alt is not None:
        neighborhood = np.arange(t-(t-t_min)*2, t+(t_max-t)*2, (t_max-t_min)*2/200)   # 200 evenly spaced points
        ax_alt.scatter(neighborhood, list(map(cost_func, neighborhood)), color='black', label='S(T)')

        ax_alt.set_title(f"Half-Thickness Fit ({attrs['material']}, {attrs['source']})")
        ax_alt.set_xlabel(f"Half-Thickness T ({'tissues' if 'tissue' in results[indx].attrs['material'] else 'inches'})")
        ax_alt.set_ylabel("S(T) (sum squared error)")
        ax_alt.legend()


    return smin, t, t_min, t_max

def overlaid(indx, bestFit, ax=None):
    inches, logits, logits_err = unwrap(results[indx])

    minInches = min(inches)
    maxInches = max(inches)

    x_values = np.arange(minInches, maxInches, 5e-3).tolist()
    y_values = [0.5**(i/bestFit) for i in x_values]

    y_content = [i.value for i in y_values]
    y_delta = [i.delta for i in y_values]

    inches, ncr, delta = zip(*sorted(zip(x_values, y_content, y_delta)))

    ax.plot(inches, ncr, color='#4e6d41', label='NCR (best fit T)')
    ax.fill_between(np.array(inches), np.array(ncr)+np.array(delta), np.array(ncr)-np.array(delta), alpha=0.25, facecolor='#95e572')

    attrs = results[i].attrs
    ax.legend()

# if __name__ == '__main__':
    # with Pool(5) as p:
        # res = p.map(process, list(range(len(results))))

    # breakpoint()

# >>>>>>> 68cb3cc3a83d6f09391e99a4e1cc04d712bebe16

data = globit("./data/*.csv")
results = [readdata(i) for i in data]

sMins = []
fitTs = []

figa, axa = plt.subplots(nrows=4, ncols=3, figsize=(20, 25))
figb, axb = plt.subplots(nrows=4, ncols=3, figsize=(20, 25))

axa_align = [e for i in axa for e in i]
axb_align = [e for i in axb for e in i]

if __name__ == '__main__':
    for i in range(0, 12):
        fig1, ax1 = plt.subplots()
        plot(i, ax1)
        plot(i, axa_align[0])
        fig1.savefig(f"out/{i}_{results[i].attrs['material']}_{results[i].attrs['source']}_ncr.png")
        fig2, ax2 = plt.subplots()
        sMin, t, tmin, tmax = process(i, ax2, axb_align[0])
        fig2.savefig(f"out/{i}_{results[i].attrs['material']}_{results[i].attrs['source']}_gradient.png")
        overlaid(i, EV(t, max(tmin,tmax)), ax1)
        overlaid(i, EV(t, max(tmin,tmax)), axa_align[0])
        axa_align.pop(0)
        axb_align.pop(0)

        figa.tight_layout()
        figb.tight_layout()


        fig1.savefig(f"out/{i}_{results[i].attrs['material']}_{results[i].attrs['source']}_ncr_overlay.png")

        figa.savefig(f"out/ncr_overlay_subplots.png")
        figb.savefig(f"out/gradient_subplots.png")

