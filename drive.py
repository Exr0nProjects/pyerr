from datacleaning import globit
from multiprocessing import Pool
from calculate import SSE, readdata, unwrap, sMinFit, RelativeIntersity, calculateSfitUncert

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sys import argv

data = globit("./data/*.csv")
results = [readdata(i) for i in data]

def plot(index):
    inches = results[index].inches
    ncr =  results[index].apply(lambda row:row["normalized_count_rate"].value, axis=1)
    delta =  results[index].apply(lambda row:row["normalized_count_rate"].delta, axis=1)

    plt.errorbar(inches, ncr, yerr=delta)

    plt.show()

# breakpoint()
# Fitting Values with Inches
# ins,outs = sMinFit(results[1], RelativeIntersity, lr = 5e-10)
# Fitting values with # of Tissues
# ins,outs = sMinFit(results[4], RelativeIntersity, lr = 5e-8)

sMins = []
fitTs = []

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

def process(indx, ax=None):
    attrs = results[indx].attrs

    print(f"processsing {attrs['material']} {attrs['source']}")

    inches, logits, logits_err = unwrap(results[indx])
    cost_func = lambda T: SSE(inches, T, logits, logits_err, RelativeIntersity)

    # t, smin = sMinFit(cost_func, lr = 5e-4 if "tissue" == attrs['material'] else 2e-7)
    t, smin = sMinFit(cost_func)

    # neighborhood = np.arange(0, 0.05, 1/1000)   # 200 evenly spaced points
    # ax.scatter(neighborhood, list(map(lambda T: SSE(inches, T, logits, logits_err, RelativeIntersity), neighborhood)), color='black', label='S(T)')
    # plt.savefig('out/near.png')
    # breakpoint()

    t_min, t_max = calculateSfitUncert(t, smin, smin+1, cost_func, ax=ax, low=1e-9, high=1e3*t)

    if ax is not None:
        neighborhood = np.arange(t-(t-t_min)*2, t+(t_max-t)*2, (t_max-t_min)*2/200)   # 200 evenly spaced points
        ax.scatter(neighborhood, list(map(cost_func, neighborhood)), color='black', label='S(T)')

        ax.set_title(f"{attrs['material']} {attrs['source']}")
        ax.set_xlabel(f"T ({attrs['material']})")
        ax.set_ylabel("S(T)")
        ax.legend()

    return smin, t, t_min, t_max

# if __name__ == '__main__':
    # with Pool(5) as p:
        # res = p.map(process, list(range(len(results))))

    # breakpoint()

# >>>>>>> 68cb3cc3a83d6f09391e99a4e1cc04d712bebe16

from concurrent.futures import ThreadPoolExecutor

if __name__ == '__main__':
    with open('out/params.tsv', 'w+') as wf, ThreadPoolExecutor(max_workers=10) as exer:
        # for i in range(0, 9):
        #     fig, ax = plt.subplots()
        #     wf.write('	'.join((results[i].attrs['material'], results[i].attrs['source'], *list(map(lambda x: str(x), process(i, ax))))) + '\n')
        #     plt.savefig(f"out/{i}_{results[i].attrs['material']}_{results[i].attrs['source']}.png")
        res = exer.map(process, range(0, 9))
        print(res)

