import math

class ErroredValue(object):
    def __init__(self, value, delta=0):
        self.value = value
        self.delta = delta

    def __add__(self, o):
        if type(o) != ErroredValue:
            o = ErroredValue(o)
        return ErroredValue((self.value+o.value), (((self.delta**2) + (o.delta**2))**0.5))

    def __radd__(self, o):
        return ErroredValue((o+self.value), (((self.delta**2) + 0)**0.5))

    def __radd__(self, o):
        return ErroredValue((o+self.value), (((self.delta**2) + 0)**0.5))

    def __sub__(self, o):
        if type(o) != ErroredValue:
            o = ErroredValue(o)
        return ErroredValue((self.value-o.value), (((self.delta**2) + (o.delta**2))**0.5))

    def __rsub__(self, o):
        return ErroredValue((o-self.value), (((self.delta**2) + 0)**0.5))

    def __rsub__(self, o):
        return ErroredValue((o-self.value), (((self.delta**2) + 0)**0.5))

    def __mul__(self, o):
        if type(o) != ErroredValue:
            o = ErroredValue(o)
        return ErroredValue((self.value*o.value), (self.value*o.value)*(((self.delta/self.value)**2 + (o.delta/o.value)**2)**0.5))

    def __rmul__(self, o):
        return ErroredValue((o*self.value), (o*self.value)*(((self.delta/self.value)**2 + 0)**0.5))
      
    def __truediv__(self, o):
        if self is o:
            return ErroredValue((self.value/o.value), 0)
        if type(o) != ErroredValue:
            o = ErroredValue(o)
        return ErroredValue((self.value/o.value), (self.value/o.value)*(((self.delta/self.value)**2 + (o.delta/o.value)**2)**0.5))

    def __rtruediv__(self,o):
        return ErroredValue((o/self.value), (o/self.value)*(((self.delta/self.value)**2)**0.5))

    # https://physics.stackexchange.com/questions/411879/how-to-calculate-the-percentage-error-of-ex-if-percentage-error-in-measuring
    def __rpow__(self, a): 
        return ErroredValue(a**(self.value), (0.5**self.value)*math.log(a, math.e)*self.delta)

    def __str__(self):
        return f'{self.value:.6f}±{self.delta:.6f}'

    def __repr__(self):
        return f'<ErroredValue {self.value:.6f}±{self.delta:.6f} at {hex(id(self))}>'

    @property
    def percentDelta(self):
        return self.delta/self.value

    @staticmethod
    def ln(a):
        return ErroredValue(math.log(a.value, math.e), ((a.delta)/a.value))
