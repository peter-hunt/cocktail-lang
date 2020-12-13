from copy import deepcopy

from .error import throw


class Type:
    pass


class ModuleType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, env):
        self.env = deepcopy(env)

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

    def __lshift__(self, other):
        if isinstance(other, NumberType):
            if self.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in << operations', line=True)
            if other.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in << operations', line=True)
            return NumberType(int(self.value) << int(other.value))
        else:
            return NotImplemented

    def __rshift__(self, other):
        if isinstance(other, NumberType):
            if self.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in >> operations', line=True)
            if other.value % 1 != 0:
                throw(self.value.info, self.value.token, 'TypeError',
                      'floats cannot be in >> operations', line=True)
            return NumberType(int(self.value) >> int(other.value))
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
    # ----- Initialization Methods ----- #
    def __init__(self, id):
        self.id = id


class ArgType:
    # ----- Initialization Methods ----- #
    def __init__(self, arg):
        self.arg = arg


class ArgumentsType:
    # ----- Initialization Methods ----- #
    def __init__(self, posonlyargs=None, args=None, vararg=None,
                 kwonlyargs=None, kw_defaults=None, kwarg=None, defaults=None):
        self.posonlyargs = [] if posonlyargs is None else posonlyargs
        self.args = [] if args is None else args
        self.vararg = vararg
        self.kwonlyargs = [] if kwonlyargs is None else kwonlyargs
        self.kw_defaults = [] if kw_defaults is None else kw_defaults
        self.kwarg = kwarg
        self.defaults = [] if defaults is None else defaults
        self.body = [] if body is None else body


class FunctionType:
    # ----- Initialization Methods ----- #
    def __init__(self, name=None, args=None, body=None, qualname=None):
        self.name = '<anonymous>' if name is None else name
        self.args = ArgumentsType() if args is None else args
        self.body = [] if body is None else body
        self.qualname = self.name if qualname is None else qualname

    # ----- Informal Methods ----- #
    def __repr__(self):
        return f'<function {self.name} at {id(self):#x}>'


class BuiltinFunctionType:
    # ----- Initialization Methods ----- #
    def __init__(self):
        self.name = '<anonymous>'
        self.args = ArgumentsType()

    # ----- Informal Methods ----- #
    def __repr__(self):
        return f'<built-in function {self.name}>'

    # ----- Functional Methods ----- #
    def __call__(self):
        pass


class PrintFunction:
    # ----- Initialization Methods ----- #
    def __init__(self):
        self.name = 'print'
        self.args = ArgumentsType()

    # ----- Functional Methods ----- #
    def __call__(self):
        pass


RESERVED = {
    'false': BooleanType(False),
    'true': BooleanType(True),
    'none': NoneType(),
}

DEFAULT_ENV = {
    # 'print': BuiltinFunctionType('print'),
}
