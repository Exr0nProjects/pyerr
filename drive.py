from datacleaning import globit
from calculate import process


data = globit("./data/*.csv")
results = [process(i) for i in data]

breakpoint()

