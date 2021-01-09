from copy import deepcopy
from re import match

from .error import throw


__all__ = [
    'Type',
    'ModuleType',
    'BooleanType',
    'NoneType',
    'NumberType',
    'StringType',
    'TupleType',
    'ListType',
    'NameType',
    'SliceType',
    'ArgType',
    'ArgumentsType',
    'FunctionType',
    'BuiltinFunctionType',

    'true',
    'false',
    'none',

    'RESERVED',
    'DEFAULT_ENV',
    'CONSTRUCTOR_TYPES',
]


class Type:
    pass


class ModuleType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, env, /):
        self.env = deepcopy(env)

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'Module({self.env})'


class BooleanType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, value, /):
        self.value = value

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return 'true' if self.value else 'false'

    # ----- Transformation Methods ----- #
    def __hash__(self, /):
        return hash(self.value)

    def __bool__(self, /):
        return self.value

    def __neg__(self, /):
        return NumberType(-self.value)

    def __pos__(self, /):
        return NumberType(+self.value)

    def __invert__(self, /):
        return BooleanType(not self.value)

    # ----- Bitwise Calculation Methods ----- #
    def __and__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value & other.value)
        else:
            return NotImplemented

    def __or__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value | other.value)
        else:
            return NotImplemented

    def __xor__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value ^ other.value)
        else:
            return NotImplemented

    # ----- Inner Operations ----- #
    @classmethod
    def construct(cls, obj=None, /, *, env):
        if obj is None:
            return cls(False)
        else:
            return cls(True if obj.eval(env=env) else False)


class NoneType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, /):
        pass

    # ----- Transformation Methods ----- #
    def __hash__(self, /):
        return hash(None)

    def __bool__(self, /):
        return False

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return 'none'


class NumberType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, value, /):
        self.value = value

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        if self.value % 1 == 0:
            return f'{self.value:.0f}'
        else:
            return f'{self.value}'

    # ----- Transformation Methods ----- #
    def __hash__(self, /):
        return hash(self.value)

    def __bool__(self, /):
        return True if self.value else False

    def __neg__(self, /):
        return NumberType(-self.value)

    def __pos__(self, /):
        return self

    def __invert__(self, /):
        if self.value % 1 == 0:
            return NumberType(~int(self.value))
        else:
            throw(self.value.info, self.value.token, 'TypeError',
                  'floats cannot be inverted', line=True)

    # ----- Comparison Methods ----- #
    def __lt__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value < other.value)
        else:
            return NotImplemented

    def __le__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value <= other.value)
        else:
            return NotImplemented

    def __eq__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value == other.value)
        else:
            return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value != other.value)
        else:
            return NotImplemented

    def __gt__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value > other.value)
        else:
            return NotImplemented

    def __ge__(self, other, /):
        if isinstance(other, NumberType):
            return BooleanType(self.value >= other.value)
        else:
            return NotImplemented

    # ----- Calculation Methods ----- #
    def __add__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value + other.value)
        else:
            return NotImplemented

    def __sub__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value - other.value)
        else:
            return NotImplemented

    def __mul__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value * other.value)
        else:
            return NotImplemented

    def __truediv__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value / other.value)
        else:
            return NotImplemented

    def __floordiv__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value // other.value)
        else:
            return NotImplemented

    def __mod__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value % other.value)
        else:
            return NotImplemented

    def __pow__(self, other, /):
        if isinstance(other, NumberType):
            return NumberType(self.value ** other.value)
        else:
            return NotImplemented

    def __lshift__(self, other, /):
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

    def __rshift__(self, other, /):
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
    def __and__(self, other, /):
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

    def __xor__(self, other, /):
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

    def __or__(self, other, /):
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

    # ----- Inner Operations ----- #
    @classmethod
    def construct(cls, obj=None, /, *, env):
        if obj is None:
            return cls(0)

        value = obj.eval(env=env)

        if isinstance(value, BooleanType):
            return cls(+value.value)
        elif isinstance(value, NumberType):
            return cls(value.value)
        elif isinstance(value, StringType):
            if match(r'^\d+(\.(\d+)?)?([Ee][+\-]?\d+)?'
                     r'|(\d+)?\.\d+([Ee][+\-]?\d+)?$', value.value):
                return cls(eval(value.value))
            else:
                throw(obj.info, obj.token, 'ValueError',
                      f"could not convert string to float: {value.value!r}",
                      line=True)
        else:
            throw(obj.info, obj.token, 'ValueError',
                  f"Number() argument must be a string or a number, "
                  f"not '{type(value).__name__}'", line=True)


class StringType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, value, /):
        self.value = value

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'{self.value!r}'

    def __str__(self, /):
        return self.value

    # ----- Transformation Methods ----- #
    def __hash__(self, /):
        return hash(self.value)

    def __bool__(self, /):
        return True if self.value else False

    # ----- Iterable Methods ----- #
    def __len__(self, /):
        return len(self.value)

    def __getitem__(self, key, /):
        if isinstance(key, int):
            return self.value[key]
        else:
            slice = []
            for item in (key.start, key.stop, key.step):
                if isinstance(item, NumberType):
                    slice.append(int(item.value))
                else:
                    slice.append(None)
            start, stop, step = slice
            return self.value[start:stop:step]

    def __iter__(self, /):
        return iter(self.value)

    def __contains__(self, item, /):
        return item.value in self.value

    # ----- Calculation Methods ----- #
    def __add__(self, other, /):
        if isinstance(other, StringType):
            return StringType(self.value + other.value)
        else:
            return NotImplemented

    def __mul__(self, other, /):
        if isinstance(other, StringType):
            return StringType(self.value * other.value)
        else:
            return NotImplemented

    def __rmul__(self, other, /):
        if isinstance(other, StringType):
            return StringType(self.value * other.value)
        else:
            return NotImplemented

    # ----- Inner Operations ----- #
    @classmethod
    def construct(cls, obj=None, /, *, env):
        return cls('' if obj is None else f'{obj.eval(env=env)}')


class TupleType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, values, /):
        self.values = values

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'{self.values}'

    # ----- Transformation Methods ----- #
    def __bool__(self, /):
        return True if self.values else False

    # ----- Iterable Methods ----- #
    def __len__(self, /):
        return len(self.values)

    def __getitem__(self, key, /):
        if isinstance(key, int):
            return self.values[key]
        else:
            slice = []
            for item in (key.start, key.stop, key.step):
                if isinstance(item, NumberType):
                    slice.append(int(item.value))
                else:
                    slice.append(None)
            start, stop, step = slice
            return self.values[start:stop:step]

    def __iter__(self, /):
        return iter(self.values)

    def __contains__(self, item, /):
        return item in self.values

    # ----- Calculation Methods ----- #
    def __add__(self, other, /):
        if isinstance(other, TupleType):
            return TupleType(self.values + other.values)
        else:
            return NotImplemented

    def __mul__(self, other, /):
        if isinstance(other, TupleType):
            return TupleType(self.values * other.values)
        else:
            return NotImplemented

    def __rmul__(self, other, /):
        if isinstance(other, TupleType):
            return TupleType(self.values * other.values)
        else:
            return NotImplemented

    # ----- Inner Operations ----- #
    @classmethod
    def construct(cls, obj=None, /, *, env):
        return cls(() if obj is None else tuple(obj.eval(env=env)))


class ListType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, values, /):
        self.values = values

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'{self.values}'

    # ----- Transformation Methods ----- #
    def __bool__(self, /):
        return True if self.values else False

    # ----- Iterable Methods ----- #
    def __len__(self, /):
        return len(self.values)

    def __getitem__(self, key, /):
        if isinstance(key, int):
            return self.values[key]
        else:
            slice = []
            for item in (key.start, key.stop, key.step):
                if isinstance(item, NumberType):
                    slice.append(int(item.value))
                else:
                    slice.append(None)
            start, stop, step = slice
            return self.values[start:stop:step]

    def __iter__(self, /):
        return iter(self.values)

    def __contains__(self, item, /):
        return item in self.values

    # ----- Calculation Methods ----- #
    def __add__(self, other, /):
        if isinstance(other, ListType):
            return ListType(self.values + other.values)
        else:
            return NotImplemented

    def __mul__(self, other, /):
        if isinstance(other, ListType):
            return ListType(self.values * other.values)
        else:
            return NotImplemented

    def __rmul__(self, other, /):
        if isinstance(other, ListType):
            return ListType(self.values * other.values)
        else:
            return NotImplemented

    # ----- Inner Operations ----- #
    @classmethod
    def construct(cls, obj=None, /, *, env):
        return cls([] if obj is None else [*obj.eval(env=env)])


class NameType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, id, /):
        self.id = id


class SliceType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, start, stop, step, /):
        self.start = start
        self.stop = stop
        self.step = step

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'SliceType({self.start}, {self.stop}, {self.step})'


class ArgType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, arg, /):
        self.arg = arg


class ArgumentsType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, /, *, posonlyargs=None, args=None, vararg=None,
                 kwonlyargs=None, kw_defaults=None, kwarg=None, defaults=None):
        self.posonlyargs = [] if posonlyargs is None else posonlyargs
        self.args = [] if args is None else args
        self.vararg = vararg
        self.kwonlyargs = [] if kwonlyargs is None else kwonlyargs
        self.kw_defaults = [] if kw_defaults is None else kw_defaults
        self.kwarg = kwarg
        self.defaults = [] if defaults is None else defaults


class FunctionType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, /, name=None, args=None, body=None, *, qualname=None):
        self.name = '<anonymous>' if name is None else name
        self.args = ArgumentsType() if args is None else args
        self.body = [] if body is None else body
        self.qualname = self.name if qualname is None else qualname

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'<function {self.qualname} at {id(self):#x}>'

    # ----- Functional Methods ----- #
    def __call__(self, arguments, /):
        pass


class BuiltinFunctionType(Type):
    # ----- Initialization Methods ----- #
    def __init__(self, /):
        self.name = '<anonymous>'
        self.args = ArgumentsType()

    # ----- Informal Methods ----- #
    def __repr__(self, /):
        return f'<built-in function {self.name}>'

    # ----- Functional Methods ----- #
    def __call__(self, /):
        pass


class PrintFunction(BuiltinFunctionType):
    # ----- Initialization Methods ----- #
    def __init__(self, /):
        self.name = 'print'
        self.args = ArgumentsType()

    # ----- Functional Methods ----- #
    def __call__(self, /):
        pass


false = BooleanType(False)
true = BooleanType(True)
none = NoneType()


RESERVED = {
    'false': false,
    'true': true,
    'none': none,
}

DEFAULT_ENV = {
    # 'print': BuiltinFunctionType('print'),
}


CONSTRUCTOR_TYPES = {
    'Boolean': BooleanType,
    'Number': NumberType,
    'String': StringType,
    'Tuple': TupleType,
    'List': ListType,
}
