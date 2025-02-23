from ErrorProp import ErroredValue as val
from math import pi, sqrt
from mpmath import mp
mp.dps = 4

x = val(17.78e-2, 0.02e-2) # cm

hc = val('12400e-10')  # eV meter
mc2 = val(0.511e6) # eV
V = val(8e3)     # V
e = val(1) # normalized units?  

#l = hc/((2*mc2*e*V)**0.5)
lam = lambda V: hc/((2*mc2*e*V)**0.5)
#print('lambda', l)

k1_graphite = 4*pi/sqrt(3)
k2_graphite = 4*pi
k1_aluminum = sqrt(3)*2*pi
k2_aluminum = 4*pi
k3_aluminum = 4*pi*sqrt(2)

a0_graphite = 0.24612e-9
a0_aluminum = 4.050e-10

radius = lambda l: x * k1_aluminum/(2*pi) * l / a0_aluminum
print(radius(lam(8e3)))

for V in [4e3, 6e3, 7e3, 8e3]:
    l = lam(V)
    r = radius(l)
    print(f'{V} volts -> {r*100 * 2} cm')

print('\n'*4)

# finding planks constant
a0 = a0_graphite
khat = k1_graphite
b = val(0.101315, 0.00241144)

fit_results = [
    ['k1 graphite', a0_graphite, k1_graphite, val(0.101315, 0.00241144)],
    ['k2 graphite', a0_graphite, k2_graphite, val(0.0356676, 0.000607506)],
    ['k1 aluminum', a0_aluminum, k1_aluminum, val(0.113423, 0.00399905)],
    ['k2 aluminum', a0_aluminum, k2_aluminum, val(0.0476964, 0.00157462)]
]

# fixing units
mc2 = val(0.511e6) # eV
eV = val('1.602e-19') # eV/joule
e = val('1.602e-19')    # coulomb
e = val('1.60217663e-19')
c = val('2.99792e8')

for name, a0, khat, b in fit_results:

    #V = 8e3
    #r = radius(lam(V))
    #b = 1 / (r**2  * V)
    #print('theory b', b)

    #b = 1.15

    h = (a0 * (2 * mc2 * eV*e)**0.5)/(c * b**0.5) * 2*pi/(khat * x)
    print(name, 'planks const', h)


# final planks constant
#b = val(359.646, 2.84361)
b = val(118.54, 0.5868)
h = ((2 * mc2 * eV*e)**0.5 * 1e-9) / (c * b**0.5 * x)
print('\n'*3)
print('final planks const', h)
