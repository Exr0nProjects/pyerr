import pickle

from datacleaning import globit
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

print(len(results))

_, indx = argv
indx = int(indx)
result = results[indx]
t, smin = sMinFit(result, RelativeIntersity, lr = 2e-10, epochs=int(2e9))

sMins.append(smin)
fitTs.append(t)

with open(f"out/result_{indx}.bin", "wb") as wb:
    pickle.dump({"sMins": sMins, "fitTs": fitTs, "results":results}, wb)
//=======
//sMinFit(results[7], RelativeIntersity)
//>>>>>>> Stashed changes

breakpoint()
