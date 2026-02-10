class DimensionError (Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'




class Vector:
    def __init__(self, *vals):
        if type(vals[0]) in (list, tuple, set, iter,map):
            vals = list(vals[0])
            if type(vals[0]) in (int, float, complex):
                self.values = list(vals)
            else:
                raise ValueError("Types outside of lists or numbers are undefined")
        elif type(vals[0]) in (int, float, complex):
            self.values = list(vals)
        elif type(vals[0]) == Vector:
            self.values = vals[0].values
        else:
            raise ValueError("Types outside of lists or numbers are undefined")
        self.dim = len(self.values)

    def __add__(self, vector):
        if self.dim != vector.dim:
            raise DimensionError("Cannot add vectors of different dimension")
        return Vector(map(lambda a, b: a+b,self.values,vector.values))

    def __sub__(self, vector):
        if self.dim != vector.dim:
            raise DimensionError("Cannot add vectors of different dimension")
        return Vector(map(lambda a, b: a-b,self.values,vector.values))

    def __mul__(self, scalar):
        return Vector(map(lambda a: a*scalar, self.values))
    
    def __truediv__(self, scalar):
        return Vector(map(lambda a: a/scalar, self.values))

    def __rmul__(self, scalar):
        Vector(map(lambda a: a*scalar, self.values))

    def __xor__(self, vector):
        if self.dim != vector.dim:
            raise DimensionError("Cannot add vectors of different dimension")
        return sum(map(lambda a, b: a*b,self.values,vector.values))

    def __pow__(self, vector):
        if not (self.dim in [3, 7]):
            raise DimensionError("Binary cross-product not defined for dimensions outside of 3 or 7")
        elif self.dim != vector.dim:
            raise DimensionError("Cannot cross-product vectors of different dimension")
        elif self.dim == 7:
            raise NotImplementedError("Crossproduct of dimension 7 not implemented yet")
        return Vector([(self.values[1] * vector.values[2]) - (self.values[2] * vector.values[1]), (self.values[2] * vector.values[0]) - (self.values[0] - vector.values[2]), (self.values[0] * vector.values[1]) - (self.values[1] * vector.values[0])])

    def __str__(self):
        result = ""
        for value in self.values:
            result += str(value) + ","
        result = result.rstrip(",")
        return f'({result})'
    
    def __abs__(self):
        return sum(map(lambda a: a**2, self.values))**0.5

    def __eq__(self, vector):
        return False if self.dim != vector.dim else self.values == vector.values