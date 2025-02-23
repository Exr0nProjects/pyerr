# prelab

from ErrorProp import ErroredValue as val
from mpmath import mp

mp.dps = 6

e0 = val('8.854e-12')       # coulomb / (meter volt)
d = val(0.309e-2, 0.001e-2) # meter
r = val(3.073e-2, 0.001e-2) # meter
g = val(979.6e-2)
m = val(20e-6) # kg

k = (2 * d**2 * g) / (mp.pi * r**2 * e0)

V = (k*m)**0.5

#print('mass: ', m*1e6, 'mg')

#print(V)

#print('% error of k:', k.delta / k.value)
#print('% error of V:', V.delta / V.value)

# data analysis
d = val(0.309e-2, 0.005e-4) # m
r = val(3.073e-2, 0.001e-2) # m
g = val(979.57e-2, 0.01e-2) # m/s2
b = val(7041.81e6, 10.526e6)    # V2/mg

e0 = 2 * d**2 * g / (mp.pi * r**2 * b)   # m2 (m/s2) / ( m2 V2/mg ) = m3/s2 mg/m2V2 = m/s2 kg/V2
print('e0', e0)

c = 1 / (4*mp.pi*1e-7 * e0)**0.5
print('c', c)
