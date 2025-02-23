from ErrorProp import ErroredValue as val
from mpmath import mp
mp.dps = 6
import numpy as np

permanant_magnet = val(383.56, 0.185)
print(permanant_magnet / 10)

c = val(299_792_458, 0)

d_ = np.array([13.1, 13.1, 13.2, 13.2, 13.2])
d = val(float(d_.mean()), float(d_.std())) * 1e-3   # meters 

b_fit = val(788.837, 1.642) * 1e-3 # tesla per delta m
b_fit_limited = val(797.594, 5.19284) * 1e-3
b_fit = b_fit_limited 

epm = 2*mp.pi * c / d * (1/b_fit)
print(epm)
print('sources:')
print('d', d*1e3)
print('b_fit', b_fit * 1e3)


# hall probe drift?
before = np.array([54.3, 54.5, 54.4, 54.4, 54.2])
after = np.array([53.5, 54.0, 54.1, 54.2, 53.7, 53.8])

print('before', before.mean(), before.std())
print('after', after.mean(), after.std())
print('delta', after.mean() - before.mean(), (after.mean() - before.mean()) / before.mean())


before = val(before.mean(), before.std()) /10
after = val(after.mean(), after.std()) /10
print('before', before, 'after', after)
print((after - before) / before)

