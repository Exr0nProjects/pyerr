from datacleaning import globit
from multiprocessing import Pool
from calculate import process, sMinFit, RelativeIntersity

import matplotlib.pyplot as plt

from sys import argv

data = globit("./data/*.csv")
results = [process(i) for i in data]

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

def process(indx):
    t, smin = sMinFit(results[indx], RelativeIntersity, lr = 5e-4 if "tissue" == results[indx].attrs["material"] else 2e-8)

    return [smin, t]

# if __name__ == '__main__':
    # with Pool(5) as p:
        # res = p.map(process, list(range(len(results))))

    # breakpoint()

# >>>>>>> 68cb3cc3a83d6f09391e99a4e1cc04d712bebe16
