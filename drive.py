from datacleaning import globit
from multiprocessing import Pool
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
# ins,outs = sMinFit(results[4], RelativeIntersity, lr = 5e-8)

sMins = []
fitTs = []

# for indx, result in enumerate(results):
    # print(result.attrs["material"], result.predicted_halfthickness.apply(lambda row:row.value).mean())

def process(indx):
    t, smin = sMinFit(results[indx], RelativeIntersity, lr = 5e-4 if "tissue" == results[indx].attrs["material"] else 2e-8)

    return [smin, t]

# if __name__ == '__main__':
    # with Pool(5) as p:
        # res = p.map(process, list(range(len(results))))

    # breakpoint()

