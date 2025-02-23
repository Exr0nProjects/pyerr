# experiment 2: compute f0, Q
from ErrorProp import ErroredValue as val

from mpmath import mp
mp.dps = 6

R = val(49.82, percent_err=0.2) 
L = val(10.320e-3, percent_err=0.5)
C = val(9.557e-9, percent_err=0.2)
Cp = val(9.557e-9, percent_err=0.2)
R_L = val(1.27, percent_err=0.2)

Q_phase = val(17.4283, 0.00380573)

#a = val('1e12000', 1)
#print(a*a)

# analysis with measured values
#print(1/R)
#print((L/C)**0.5)
#print(1/R * (L/C)**0.5)

# analysis to find R_L needed
print(1/Q_phase * (L/C)**0.5)

# analysis with R_L and C'
#print(1/(R + R_L) * (L/C)**0.5)





#Q = val(17.4283, 0.0038573)
#w0 = val(16027.5, 0.112035)

#print(w0 / Q)
