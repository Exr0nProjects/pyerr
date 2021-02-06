import tqdm
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from ErrorProp import ErroredValue as EV

GOOD_ENOUGH = 1e-9
OFF_FACTOR = 10

# one dimensional gradient descent
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

# one dimensional parameter uncertanty
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

# cost functions
def SSE(function, indicies, prediction, logits, logits_error=None):
    ri = function(prediction, indicies)
    if logits_error is not None:
        return ((logits-ri)**2/logits_error**2).sum()
    else:
        return ((logits-ri)**2).sum()

