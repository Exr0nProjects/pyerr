class ErroredValue(object):
    def __init__(self, value, delta):
        self.value = value
        self.delta = delta

    def __add__(self, o): 
        return ErroredValue((self.value+o.value), (((self.delta**2) + (o.delta**2))**0.5))

    def __sub__(self, o):
        return ErroredValue((self.value-o.value), (((self.delta**2) + (o.delta**2))**0.5))

    def __mul__(self, o):
        return ErroredValue((self.value*o.value), (self.value*o.value)*(((self.delta/self.value)**2 + (o.delta/o.value)**2)**0.5))

    def __div__(self, o):
        return ErroredValue((self.value/o.value), (self.value/o.value)*(((self.delta/self.value)**2 + (o.delta/o.value)**2)**0.5))







