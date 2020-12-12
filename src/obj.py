from .error import throw


class Type:
    pass


class ModuleType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, env):
        self.env = env

    # ----- Informal Methods ----- #
    def __repr__(self):
        return f'Module({self.env})'


class BooleanType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, value):
        self.value = value

    # ----- Informal Methods ----- #
    def __repr__(self):
        return 'true' if self.value else 'false'

    # ----- Transformation Methods ----- #
    def __bool__(self):
        return self.value

    def __inv__(self):
        return BooleanType(not self.value)

    # ----- Bitwise Calculation Methods ----- #
    def __and__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value & other.value)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value | other.value)
        else:
            return NotImplemented

    def __xor__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value ^ other.value)
        else:
            return NotImplemented


class NoneType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self):
        pass

    # ----- Informal Methods ----- #
    def __repr__(self):
        return 'none'


class NumberType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, value):
        self.value = value

    # ----- Informal Methods ----- #
    def __repr__(self):
        if self.value % 1 == 0:
            return f'{self.value:.0f}'
        else:
            return f'{self.value}'

    # ----- Transformation Methods ----- #
    def __neg__(self):
        return NumberType(-self.value)

    def __pos__(self):
        return self

    def __invert__(self):
        if self.value % 1 == 0:
            return NumberType(~int(self.value))
        else:
            throw(self.value.info, self.value.token, 'TypeError',
                  'floats cannot be inverted', line=True)

    # ----- Comparison Methods ----- #
    def __lt__(self, other):
        if isinstance(other, NumberType):
            return BooleanType(self.value < other.value)
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, NumberType):
            return BooleanType(self.value <= other.value)
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, NumberType):
            return BooleanType(self.value == other.value)
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, NumberType):
            return BooleanType(self.value != other.value)
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, NumberType):
            return BooleanType(self.value > other.value)
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, NumberType):
            return BooleanType(self.value >= other.value)
        else:
            return NotImplemented

    # ----- Calculation Methods ----- #
    def __add__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value + other.value)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value - other.value)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value * other.value)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value / other.value)
        else:
            return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value // other.value)
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value % other.value)
        else:
            return NotImplemented

    def __pow__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value ** other.value)
        else:
            return NotImplemented

    # ----- Bitwise Calculation Methods ----- #
    def __and__(self, other):
        if isinstance(other, NumberType):
            if self.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in & operations', line=True)
            if other.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in & operations', line=True)
            return NumberType(int(self.value) & int(other.value))
        else:
            return NotImplemented

    def __xor__(self, other):
        if isinstance(other, NumberType):
            if self.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in ^ operations', line=True)
            if other.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in ^ operations', line=True)
            return NumberType(int(self.value) ^ int(other.value))
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, NumberType):
            if self.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in | operations', line=True)
            if other.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in | operations', line=True)
            return NumberType(int(self.value) | int(other.value))
        else:
            return NotImplemented


class StringType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, value):
        self.value = value

    # ----- Informal Methods ----- #
    def __repr__(self):
        return f'{self.value!r}'

    def __str__(self):
        return self.value

    # ----- Calculation Methods ----- #
    def __add__(self, other):
        if isinstance(other, StringType):
            return StringType(self.value + other.value)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value * other.value)
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, NumberType):
            return NumberType(self.value * other.value)
        else:
            return NotImplemented


class NameType:
    def __init__(self, id):
        self.id = id


RESERVED = {
    'false': BooleanType(False),
    'true': BooleanType(True),
    'none': NoneType(),
}
