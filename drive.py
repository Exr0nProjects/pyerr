from datacleaning import globit
from calculate import process, sMinFit, RelativeIntersity

import matplotlib.pyplot as plt

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
ins,outs = sMinFit(results[4], RelativeIntersity, lr = 5e-8)

breakpoint()

