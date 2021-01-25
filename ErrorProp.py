class ErroredValue(object):
    def __init__(self, value, delta=0):
        self.value = value
        self.delta = delta

    def __add__(self, o):
        if type(o) == ErroredValue:
            return ErroredValue((self.value+o.value), (((self.delta**2) + (o.delta**2))**0.5))
        else:
            return ErroredValue((self.value+o), (((self.delta**2) + 0)**0.5))

    def __radd__(self, o):
        return ErroredValue((o+self.value), (((self.delta**2) + 0)**0.5))

    def __sub__(self, o):
        if type(o) == ErroredValue:
            return ErroredValue((self.value-o.value), (((self.delta**2) + (o.delta**2))**0.5))
        else:
            return ErroredValue((self.value-o), (((self.delta**2) + 0)**0.5))

    def __rsub__(self, o):
        return ErroredValue((o-self.value), (((self.delta**2) + 0)**0.5))

    def __mul__(self, o):
        if type(o) == ErroredValue:
            return ErroredValue((self.value*o.value), (self.value*o.value)*(((self.delta/self.value)**2 + (o.delta/o.value)**2)**0.5))
        else:
            return ErroredValue((self.value*o), (self.value*o)*(((self.delta/self.value)**2 + 0)**0.5))

    def __rmul__(self, o):
        return ErroredValue((o*self.value), (o*self.value)*(((self.delta/self.value)**2 + 0)**0.5))

    def __truediv__(self, o):
        if type(o) == ErroredValue:
            return ErroredValue((self.value/o.value), (self.value/o.value)*(((self.delta/self.value)**2 + (o.delta/o.value)**2)**0.5))
        else:
            return ErroredValue((self.value/o), (self.value/o)*(((self.delta/self.value)**2)**0.5))

    def __rtruediv__(self,o):
        return ErroredValue((o/self.value), (o/self.value)*(((self.delta/self.value)**2)**0.5))

    def __str__(self):
        return f'{self.value:.2f}±{self.delta:.2f}'

    def __repr__(self):
        return f'<ErroredValue {self.value:.2f}±{self.delta:.2f} at {hex(id(self))}>'

