from ErrorProp import ErroredValue as val
from mpmath import mp
mp.dps = 6
import numpy as np

temp_air = val([24.11, 24.27]) + 273.15   # temperatures before and after
fringes_air_red = val([153.1, 153.2, 152.7, 153.0, 152.6])
fringes_air_grn = val([178.9, 179.1, 179.0, 178.6, 179.2])

temp_co2 = val([24.82, 24.50]) + 273.15
fringes_co2_red = val([233.1, 233.1, 233.0, 233.1, 233.0])
fringes_co2_grn = val([273.2, 272.1, 273.1, 273.0, 273.0])

temp_hel = val([24.59, 24.58]) + 273.15
fringes_hel_red = val([19.6, 19.6, 19.2, 19.1, 19.3, 19.1])
fringes_hel_grn = val([22.4, 22.5, 22.4, 22.2, 22.4])

P = val([742.7, 742.5, 743.5])  # mm Hg? / Torr, assuming normal local gravity
L = val([7.3567, 7.3599, 7.3598, 7.3656, 7.3544]) * 2.54 / 100 # meters 
print('L', L)

l_vac_red = val(632.99e-9) # meters
l_vac_grn = val(543.52e-9) # meters 


n_minus_1 = lambda l_vac, cnt: 0.5 * cnt * l_vac / L

conditions = [
    ('air', 'red', temp_air, l_vac_red, fringes_air_red),
    ('air', 'grn', temp_air, l_vac_grn, fringes_air_grn),
    ('co2', 'red', temp_co2, l_vac_red, fringes_co2_red),
    ('co2', 'grn', temp_co2, l_vac_grn, fringes_co2_grn),
    ('He',  'red', temp_hel, l_vac_red, fringes_hel_red),
    ('He',  'grn', temp_hel, l_vac_grn, fringes_hel_grn),
]


for gas, color, temp, l_vac, cnt in conditions:
    print(f'{gas} {color} -> ', n_minus_1(l_vac, cnt))


# at std temp and pressure
print('\n'*3)
target_P = 760      # Torr 
target_T = 273.15   # kelvin 

n_minus_1s = []
for gas, color, temp, l_vac, cnt in conditions:
    # N prop P/T
    n_1 = n_minus_1(l_vac, cnt) / (P/temp) * (target_P / target_T)
    print(f'at STP: {gas} {color} -> ', n_1)
    n_minus_1s.append(n_1)


# calculate l_0 and n_e
print('\n'*3)
r_e = val('2.82e-15')     # meters 
N = val('2.686e25')      # per meters cubed 

ns_ls_by_gas = [
    ('air', n_minus_1s[0], l_vac_red, n_minus_1s[1], l_vac_grn),
    ('CO2', n_minus_1s[2], l_vac_red, n_minus_1s[3], l_vac_grn),
    ('He',  n_minus_1s[4], l_vac_red, n_minus_1s[5], l_vac_grn),  # doesn't work ? 
]
for gas, n1, l1, n2, l2 in ns_ls_by_gas:
    a1 = 2*np.pi / (N * r_e) * n1 
    a2 = 2*np.pi / (N * r_e) * n2 
    c1 = 1/l1**2
    c2 = 1/l2**2

    print('   ', a1, a2, c1, c2)

    x = (a1*c1 - a2*c2) / (a1 - a2)
    y = a1*a2*(c1-c2) / (a1 - a2)

    print(f'{gas} l_0 = {1/(x**0.5)}, n_e = {y}')
