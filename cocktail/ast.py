from builtins import type as builtin_type
from copy import deepcopy
from dataclasses import dataclass, field
from re import compile as re_compile, error as re_error, match as re_match
from typing import (
    Dict as TypingDict, List as TypingList, Tuple as TypingTuple, Union
)

from .rply.token import BaseBox, Token

from .error import throw
from .obj import *


__all__ = [
    'Ast',

    'Module',

    'Assign',
    'AugAssign',
    'Construct',

    'Expr',
    'Constant',
    'Number',
    'String',
    'Tuple',
    'List',
    'Slice',

    'ExprContent',
    'Load',
    'Store',

    'Name',

    'BinOp',
    'Operator',
    'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift', 'RShift',
    'BitAnd', 'BitXor', 'BitOr',

    'UnaryOp',
    'UnaryOperator',
    'Invert', 'Not', 'UAdd', 'USub',

    'InplaceUnaryOp',
    'InplaceUnaryOperator',
    'PostIncrement', 'PostDecrement', 'PreIncrement', 'PreDecrement',

    'Compare',
    'CmpOp',
    'Eq', 'Gt', 'GtE', 'In', 'Is', 'IsNot', 'Lt', 'LtE', 'NotEq', 'NotIn',

    'GetItem',
    'If', 'For', 'ForOf', 'While',

    'ScopeStmt',
    'Break', 'Continue', 'Exit',

    'FunctionDef', 'Call',
    'FunctionStmt',
    'Global', 'Return', 'Nonlocal',
    'Arg', 'Arguments',

    'BUILTIN_FUNCTIONS',
]


class Ast(BaseBox):
    _fields = ()
    info = None


Name = type('Name', (Ast,), {})
Operator = type('Operator', (Ast,), {})
UnaryOperator = type('UnaryOperator', (Ast,), {})
InplaceUnaryOperator = type('InplaceUnaryOperator', (Ast,), {})
CmpOp = type('CmpOp', (Ast,), {})
Arguments = type('Arguments', (Ast,), {})


@dataclass
class Module(Ast):
    _fields = ('body',)
    body: list = field(default_factory=list)

    def __init__(self, body=None):
        self.body = [] if body is None else body

    def eval(self, /):
        env = DEFAULT_ENV.copy()

        for stmt in self.body:
            result = stmt.eval(env=env)
            if isinstance(result, ScopeStmt) and not isinstance(result, Exit):
                throw(stmt.info, stmt.token, 'SyntaxError',
                      f"cannot use '{type(stmt).__name__.lower()}'"
                      f" outside loop")
            elif isinstance(result, FunctionStmt):
                throw(stmt.info, stmt.token, 'SyntaxError',
                      f"cannot use '{type(stmt).__name__.lower()}'"
                      f" outside function definition")

        return ModuleType(env)


@dataclass
class Assign(Ast):
    _fields = ('target', 'value')
    target: Name
    value: Ast

    def eval(self, /, *, env):
        value = self.value.eval(env=env)
        env[self.target.eval(env=env).id] = value
        return value


@dataclass
class AugAssign(Ast):
    _fields = ('target', 'op', 'value')
    target: Name
    op: Operator
    value: Ast

    def eval(self, /, *, env):
        value = self.op.eval(env[self.target.eval(env=env).id], self.value,
                             env=env)
        env[self.target.eval(env=env).id] = value
        return value


@dataclass
class Construct(Ast):
    _fields = ('type', 'args')
    type: builtin_type
    args: TypingTuple[Ast]

    def eval(self, /, *, env):
        return self.type.construct(*self.args, env=env)


@dataclass
class Expr(Ast):
    _fields = ('value',)
    value: Ast

    def eval(self, /, *, env):
        return self.value.eval(env=env)


@dataclass
class Constant(Ast):
    _fields = ('token',)
    token: Token

    def eval(self, /, *, env):
        return RESERVED[self.token.value]


@dataclass
class Number(Ast):
    _fields = ('token',)
    token: Token

    def eval(self, /, *, env):
        return NumberType(float(self.token.value))


@dataclass
class String(Ast):
    _fields = ('token',)
    token: Token

    def eval(self, /, *, env):
        return StringType(eval(self.token.value))


@dataclass
class Tuple(Ast):
    _fields = ('values',)
    values: tuple

    def eval(self, /, *, env):
        return TupleType(tuple(value.eval(env=env) for value in self.values))


@dataclass
class List(Ast):
    _fields = ('values',)
    values: list

    def eval(self, /, *, env):
        return ListType([value.eval(env=env) for value in self.values])


@dataclass
class Slice(Ast):
    _fields = ('start', 'stop', 'step')
    start: Ast
    stop: Ast
    step: Ast

    def __init__(self, start, stop, step, /):
        self.start = start
        self.stop = stop
        self.step = step

        self.token = start.token

    def eval(self, /, *, env):
        start = none if self.start is none else self.start.eval(env=env)
        stop = none if self.stop is none else self.stop.eval(env=env)
        step = none if self.step is none else self.step.eval(env=env)

        if not isinstance(start, NoneType):
            if not isinstance(start, NumberType):
                throw(self.start.info, self.start.token, 'TypeError',
                      f'Slice indices must be integers, '
                      f'not {type(start).__name__}', line=True)
            if start.value % 1 != 0:
                throw(self.start.info, self.start.token, 'TypeError',
                      f'Slice indices must be integers, not float', line=True)

        if not isinstance(stop, NoneType):
            if not isinstance(stop, NumberType):
                throw(self.stop.info, self.stop.token, 'TypeError',
                      f'Slice indices must be integers, '
                      f'not {type(stop).__name__}', line=True)
            if stop.value % 1 != 0:
                throw(self.stop.info, self.stop.token, 'TypeError',
                      f'Slice indices must be integers, not float', line=True)

        if not isinstance(step, NoneType):
            if not isinstance(step, NumberType):
                throw(self.step.info, self.step.token, 'TypeError',
                      f'Slice indices must be integers, '
                      f'not {type(step).__name__}', line=True)
            if step.value % 1 != 0:
                throw(self.step.info, self.step.token, 'TypeError',
                      f'Slice indices must be integers, not float', line=True)

        return SliceType(start, stop, step)


@dataclass
class ExprContent(Ast):
    pass


@dataclass
class Load(ExprContent):
    pass


@dataclass
class Store(ExprContent):
    pass


@dataclass
class Name(Ast):
    _fields = ('token', 'id', 'ctx')
    token: Token
    ctx: ExprContent

    def __init__(self, token, ctx, /):
        self.token = token
        self.id = token.value
        self.ctx = ctx

    def eval(self, /, *, env):
        if isinstance(self.ctx, Load):
            if self.id not in env:
                throw(self.info, self.token, 'NameError',
                      f"name '{self.id}' is not found")
            return env[self.id]
        else:
            return NameType(self.id)


@dataclass
class BinOp(Ast):
    _fields = ('left', 'op', 'right')
    left: Ast
    op: Operator
    right: Ast

    def eval(self, /, *, env):
        return self.op.eval(self.left, self.right, env=env)


@dataclass
class Operator(Ast):
    @staticmethod
    def process(value, /, *, env):
        if isinstance(value, Ast):
            return value.eval(env=env)
        else:
            return value


@dataclass
class Add(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__add__') and
                (result := left_value.__add__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__radd__') and
                (result := right_value.__radd__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for +: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class Sub(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__sub__') and
                (result := left_value.__sub__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rsub__') and
                (result := right_value.__rsub__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for -: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class Mult(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__mul__') and
                (result := left_value.__mul__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rmul__') and
                (result := right_value.__rmul__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for *: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class Div(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__truediv__') and
                (result := left_value.__truediv__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rtruediv__') and
                (result := right_value.__rtruediv__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for /: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class FloorDiv(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__floordiv__') and
                (result := left_value.__floordiv__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rfloordiv__') and
                (result := right_value.__rfloordiv__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for //: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class Mod(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__mod__') and
                (result := left_value.__mod__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rmod__') and
                (result := right_value.__rmod__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for %: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class Pow(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__pow__') and
                (result := left_value.__pow__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rpow__') and
                (result := right_value.__rpow__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for **: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class LShift(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__lshift__') and
                (result := left_value.__lshift__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rlshift__') and
                (result := right_value.__rlshift__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for <<: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class RShift(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__rshift__') and
                (result := left_value.__rshift__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rrshift__') and
                (result := right_value.__rrshift__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for >>: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class BitAnd(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__and__') and
                (result := left_value.__and__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rand__') and
                (result := right_value.__rand__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for &: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class BitXor(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__xor__') and
                (result := left_value.__xor__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__rxor__') and
                (result := right_value.__rxor__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for ^: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class BitOr(Operator):
    @classmethod
    def eval(cls, left, right, /, *, env):
        left_value = cls.process(left, env=env)
        right_value = cls.process(right, env=env)

        if (hasattr(left_value, '__or__') and
                (result := left_value.__or__(right_value))
                is not NotImplemented):
            return result
        elif (hasattr(right_value, '__ror__') and
                (result := right_value.__ror__(left_value))
              is not NotImplemented):
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for |: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


@dataclass
class UnaryOp(Ast):
    op: UnaryOperator
    operand: Ast

    def eval(self, /, *, env):
        return self.op.eval(self.operand, env=env)


@dataclass
class UnaryOperator(Ast):
    pass


@dataclass
class Invert(UnaryOperator):
    @staticmethod
    def eval(operand, /, *, env):
        operand_value = operand.eval(env=env)

        if hasattr(operand_value, '__invert__'):
            return operand_value.__invert__()
        else:
            throw(operand.info, operand.token, 'TypeError',
                  f"bad operand type for unary ~: "
                  f"'{type(operand_value).__name__}'", line=True)


@dataclass
class Not(UnaryOperator):
    @staticmethod
    def eval(operand, /, *, env):
        operand_value = operand.eval(env=env)

        if hasattr(operand_value, '__bool__'):
            return ~BooleanType(operand_value)
        else:
            return BooleanType(False)


@dataclass
class UAdd(UnaryOperator):
    @staticmethod
    def eval(operand, /, *, env):
        operand_value = operand.eval(env=env)

        if hasattr(operand_value, '__pos__'):
            return operand_value.__pos__()
        else:
            throw(operand.info, operand.token, 'TypeError',
                  f"bad operand type for unary +: "
                  f"'{type(operand_value).__name__}'", line=True)


@dataclass
class USub(UnaryOperator):
    @staticmethod
    def eval(operand, /, *, env):
        operand_value = operand.eval(env=env)

        if hasattr(operand_value, '__neg__'):
            return operand_value.__neg__()
        else:
            throw(operand.info, operand.token, 'TypeError',
                  f"bad operand type for unary -: "
                  f"'{type(operand_value).__name__}'", line=True)


@dataclass
class InplaceUnaryOp(Ast):
    source: Name
    target: Name
    op: InplaceUnaryOperator

    def eval(self, /, *, env):
        return self.op.eval(self.source, self.target, env=env)


@dataclass
class InplaceUnaryOperator(Ast):
    pass


@dataclass
class PostIncrement(InplaceUnaryOperator):
    @staticmethod
    def eval(source, target, /, *, env):
        source_value = source.eval(env=env)
        one = NumberType(1)

        if (hasattr(source_value, '__add__') and
                (result := source_value.__add__(one))
                is not NotImplemented):
            env[target.eval(env=env).id] = result
            return source_value
        elif (result := one.__radd__(source_value)) is not NotImplemented:
            env[target.eval(env=env).id] = result
            return source_value
        else:
            throw(source.info, source.token, 'TypeError',
                  f"bad operand type for unary ++: "
                  f"'{type(source_value).__name__}'", line=True)


@dataclass
class PostDecrement(InplaceUnaryOperator):
    @staticmethod
    def eval(source, target, /, *, env):
        source_value = source.eval(env=env)
        one = NumberType(1)

        if (hasattr(source_value, '__sub__') and
                (result := source_value.__sub__(one))
                is not NotImplemented):
            env[target.eval(env=env).id] = result
            return source_value
        elif (result := one.__rsub__(source_value)) is not NotImplemented:
            env[target.eval(env=env).id] = result
            return source_value
        else:
            throw(source.info, source.token, 'TypeError',
                  f"bad operand type for unary --: "
                  f"'{type(source_value).__name__}'", line=True)


@dataclass
class PreIncrement(InplaceUnaryOperator):
    @staticmethod
    def eval(source, target, /, *, env):
        source_value = source.eval(env=env)
        one = NumberType(1)

        if (hasattr(source_value, '__add__') and
                (result := source_value.__add__(one))
                is not NotImplemented):
            env[target.eval(env=env).id] = result
            return result
        elif (result := one.__radd__(source_value)) is not NotImplemented:
            env[target.eval(env=env).id] = result
            return result
        else:
            throw(source.info, source.token, 'TypeError',
                  f"bad operand type for unary ++: "
                  f"'{type(source_value).__name__}'", line=True)


@dataclass
class PreDecrement(InplaceUnaryOperator):
    @staticmethod
    def eval(source, target, /, *, env):
        source_value = source.eval(env=env)
        one = NumberType(1)

        if (hasattr(source_value, '__sub__') and
                (result := source_value.__sub__(one))
                is not NotImplemented):
            env[target.eval(env=env).id] = result
            return result
        elif (result := one.__rsub__(source_value)) is not NotImplemented:
            env[target.eval(env=env).id] = result
            return result
        else:
            throw(source.info, source.token, 'TypeError',
                  f"bad operand type for unary --: "
                  f"'{type(source_value).__name__}'", line=True)


@dataclass
class Compare(Ast):
    left: Ast
    ops: TypingList[CmpOp]
    comparators: TypingList[Ast]

    def eval(self, /, *, env):
        last = self.left
        for index in range(len(self.ops)):
            if not self.ops[index].eval(
                last, self.comparators[index], env=env
            ):
                return BooleanType(False)
            last = self.comparators[index]

        return BooleanType(True)


@dataclass
class CmpOp(Ast):
    pass


@dataclass
class Eq(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if (hasattr(left_value, '__eq__') and (result := left_value.__eq__(
                right_value)) is not NotImplemented):
            return result
        elif (hasattr(right_value, '__eq__') and (result := right_value.__eq__(
                left_value)) is not NotImplemented):
            return result
        elif (hasattr(left_value, '__ne__') and (result := left_value.__ne__(
                right_value)) is not NotImplemented):
            return ~result
        elif (hasattr(right_value, '__ne__') and (result := right_value.__ne__(
                left_value)) is not NotImplemented):
            return ~result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"'==' not supported between '{type(left_value).__name__}' "
                  f"and '{type(right_value).__name__}'")


@dataclass
class Gt(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if (hasattr(left_value, '__gt__') and (result := left_value.__gt__(
                right_value)) is not NotImplemented):
            return result
        elif (hasattr(right_value, '__le__') and (result := right_value.__le__(
                left_value)) is not NotImplemented):
            return result
        elif (hasattr(left_value, '__le__') and (result := left_value.__le__(
                right_value)) is not NotImplemented):
            return ~result
        elif (hasattr(right_value, '__gt__') and (result := right_value.__gt__(
                left_value)) is not NotImplemented):
            return ~result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"'>' not supported between '{type(left_value).__name__}' "
                  f"and '{type(right_value).__name__}'")


@dataclass
class GtE(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if (hasattr(left_value, '__ge__') and (result := left_value.__ge__(
                right_value)) is not NotImplemented):
            return result
        elif (hasattr(right_value, '__lt__') and (result := right_value.__lt__(
                left_value)) is not NotImplemented):
            return result
        elif (hasattr(left_value, '__lt__') and (result := left_value.__lt__(
                right_value)) is not NotImplemented):
            return ~result
        elif (hasattr(right_value, '__ge__') and (result := right_value.__ge__(
                left_value)) is not NotImplemented):
            return ~result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"'>=' not supported between '{type(left_value).__name__}' "
                  f"and '{type(right_value).__name__}'")


@dataclass
class In(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if hasattr(right_value, '__contains__'):
            if isinstance(right_value, StringType):
                if isinstance(left_value, StringType):
                    return right_value.__contains__(left_value)
                else:
                    throw(left.info, left.token, 'TypeError',
                          f"'in <StringType>' requires StringType "
                          f"as left operand, not {type(left_value).__name__}",
                          line=True)
            else:
                return right_value.__contains__(left_value)
        else:
            throw(right.info, right.token, 'TypeError',
                  f"argument of type '{type(right_value).__name__}' "
                  f"is not iterable", line=True)


@dataclass
class Is(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        return BooleanType(left.eval(env=env) is right.eval(env=env))


@dataclass
class IsNot(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        return BooleanType(left.eval(env=env) is not right.eval(env=env))


@dataclass
class Lt(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if (hasattr(left_value, '__lt__') and (result := left_value.__lt__(
                right_value)) is not NotImplemented):
            return result
        elif (hasattr(right_value, '__ge__') and (result := right_value.__ge__(
                left_value)) is not NotImplemented):
            return result
        elif (hasattr(left_value, '__ge__') and (result := left_value.__ge__(
                right_value)) is not NotImplemented):
            return ~result
        elif (hasattr(right_value, '__lt__') and (result := right_value.__lt__(
                left_value)) is not NotImplemented):
            return ~result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"'<' not supported between '{type(left_value).__name__}' "
                  f"and '{type(right_value).__name__}'")


@dataclass
class LtE(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if (hasattr(left_value, '__le__') and (result := left_value.__le__(
                right_value)) is not NotImplemented):
            return result
        elif (hasattr(right_value, '__gt__') and (result := right_value.__gt__(
                left_value)) is not NotImplemented):
            return result
        elif (hasattr(left_value, '__gt__') and (result := left_value.__gt__(
                right_value)) is not NotImplemented):
            return ~result
        elif (hasattr(right_value, '__le__') and (result := right_value.__le__(
                left_value)) is not NotImplemented):
            return ~result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"'<=' not supported between '{type(left_value).__name__}' "
                  f"and '{type(right_value).__name__}'")


@dataclass
class NotEq(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if (hasattr(left_value, '__ne__') and (result := left_value.__ne__(
                right_value)) is not NotImplemented):
            return result
        elif (hasattr(right_value, '__ne__') and (result := right_value.__ne__(
                left_value)) is not NotImplemented):
            return result
        elif (hasattr(left_value, '__eq__') and (result := left_value.__eq__(
                right_value)) is not NotImplemented):
            return ~result
        elif (hasattr(right_value, '__eq__') and (result := right_value.__eq__(
                left_value)) is not NotImplemented):
            return ~result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"'!=' not supported between '{type(left_value).__name__}' "
                  f"and '{type(right_value).__name__}'")


@dataclass
class NotIn(CmpOp):
    @staticmethod
    def eval(left, right, /, *, env):
        left_value = left.eval(env=env)
        right_value = right.eval(env=env)

        if hasattr(right_value, '__contains__'):
            if isinstance(right_value, StringType):
                if isinstance(left_value, StringType):
                    return ~right_value.__contains__(left_value)
                else:
                    throw(left.info, left.token, 'TypeError',
                          f"'not in <StringType>' requires StringType "
                          f"as left operand, not {type(left_value).__name__}",
                          line=True)
            else:
                return ~right_value.__contains__(left_value)
        else:
            throw(right.info, right.token, 'TypeError',
                  f"argument of type '{type(right_value).__name__}' "
                  f"is not iterable", line=True)


@dataclass
class GetItem(Ast):
    _fields = ('obj', 'key')

    def __init__(self, obj, key, /):
        self.obj = obj
        self.key = key

    def eval(self, /, *, env):
        obj = self.obj.eval(env=env)
        key = self.key.eval(env=env)

        if hasattr(obj, '__getitem__'):
            if isinstance(key, NumberType):
                if key.value % 1 != 0:
                    throw(self.key.info, self.key.token, 'TypeError',
                          f'{type(obj).__name__} indices must '
                          f'be integers or slices, not float', line=True)
                if key.value >= len(obj):
                    throw(self.key.info, self.key.token, 'IndexError',
                          f'{type(obj).__name__} index out of range', line=True)
                return obj[int(key.value)]
            elif isinstance(key, SliceType):
                return obj[key]
            else:
                throw(self.key.info, self.key.token, 'TypeError',
                      f'{type(obj).__name__} indices must '
                      f'be integers or slices, not {type(key).__name__}',
                      line=True)
        else:
            throw(self.obj.info, self.obj.token, 'TypeError',
                  f"'{type(obj).__name__}' object is not subscriptable",
                  line=True)


@dataclass
class If(Ast):
    _fields = ('test', 'body', 'orelse')
    test: Ast
    body: TypingList[Ast]
    orelse: TypingList[Ast] = field(default_factory=list)

    def eval(self, /, *, env):
        for stmt in self.body if self.test.eval(env=env) else self.orelse:
            if isinstance(stmt, ScopeStmt):
                return stmt

            result = stmt.eval(env=env)

            if isinstance(result, ScopeStmt):
                return result


@dataclass
class For(Ast):
    _fields = ('init', 'cond', 'loop', 'body', 'orelse')
    init: Ast
    cond: Ast
    loop: Ast
    body: TypingList[Ast]
    orelse: TypingList[Ast] = field(default_factory=list)

    def eval(self, /, *, env):
        self.init.eval(env=env)

        while self.cond.eval(env=env):
            for stmt in self.body:
                if isinstance(stmt, Break):
                    return
                elif isinstance(stmt, Continue):
                    break

                result = stmt.eval(env=env)

                if isinstance(result, Exit):
                    return stmt

            self.loop.eval(env=env)

        for stmt in self.orelse:
            if isinstance(stmt, ScopeStmt):
                return stmt

            result = stmt.eval(env=env)

            if isinstance(result, ScopeStmt):
                return result


@dataclass
class ForOf(Ast):
    _fields = ('target', 'source', 'body', 'orelse')
    target: Ast
    source: Ast
    body: TypingList[Ast]
    orelse: TypingList[Ast] = field(default_factory=list)

    def eval(self, /, *, env):
        value = self.source.eval(env=env)
        target_value = self.target.eval(env=env)

        if not hasattr(value, '__iter__'):
            throw(source.info, source.token, 'TypeError',
                  f"'{type(value).__name__}' object is not iterable",
                  line=True)

        iterator = iter(value)

        try:
            while True:
                env[target_value.id] = next(iterator)

                for stmt in self.body:
                    if isinstance(stmt, Break):
                        return
                    elif isinstance(stmt, Continue):
                        break

                    result = stmt.eval(env=env)

                    if isinstance(result, Exit):
                        return stmt
        except StopIteration:
            pass

        for stmt in self.orelse:
            if isinstance(stmt, ScopeStmt):
                return stmt

            result = stmt.eval(env=env)

            if isinstance(result, ScopeStmt):
                return result


@dataclass
class While(Ast):
    _fields = ('test', 'body', 'orelse')
    test: Ast
    body: TypingList[Ast]
    orelse: TypingList[Ast] = field(default_factory=list)

    def eval(self, /, *, env):
        run_orelse = True

        while self.test.eval(env=env):
            for stmt in self.body:
                if isinstance(stmt, Break):
                    return
                elif isinstance(stmt, Continue):
                    break

                result = stmt.eval(env=env)

                if isinstance(result, Exit):
                    return stmt

        for stmt in self.orelse:
            if isinstance(stmt, ScopeStmt):
                return stmt

            result = stmt.eval(env=env)

            if isinstance(result, ScopeStmt):
                return result


@dataclass
class ScopeStmt(Ast):
    _fields = ('token',)
    token: Token

    def eval(self, /, *, env):
        pass


@dataclass
class Break(ScopeStmt):
    pass


@dataclass
class Continue(ScopeStmt):
    pass


@dataclass
class FunctionDef(Ast):
    _fields = ('name', 'args', 'body')
    name: str
    args: Arguments = field(default_factory=Arguments)
    body: list = field(default_factory=list)

    def eval(self, /, *, env):
        env[self.name] = FunctionType(self.name, self.args, self.body)


@dataclass
class Call(Ast):
    _fields = ('name', 'args', 'kwargs')
    name: Name
    args: TypingTuple[Ast]
    kwargs: TypingDict[str, Ast]

    def eval(self, /, *, env):
        func = self.name.eval(env=env)


@dataclass
class FunctionStmt(Ast):
    def eval(self, /, *, env):
        return self


@dataclass
class Global(FunctionStmt):
    _fields = ('names',)
    names: TypingList[Name]


@dataclass
class Return(FunctionStmt):
    _fields = ('value',)
    value: Ast


@dataclass
class Nonlocal(FunctionStmt):
    _fields = ('names',)
    names: TypingList[Name]


# arguments(
#         posonlyargs = [],
#         args = [arg(arg='a')],
#         vararg = arg(arg='args'),
#         kwonlyargs = [arg(arg='b')],
#         kw_defaults = [Constant(value=1, kind=None)],
#         kwarg = arg(arg='kwargs'),
#         defaults = [],
#     posonlyargs=[],
#     args=[
#         arg(arg='a'),
#         arg(arg='b'),
#     ],
#     vararg=None,
#     kwonlyargs=[],
#     kw_defaults=[],
#     kwarg=None,
#     defaults=[Constant(value=1, kind=None)],
# )

@dataclass
class Arg(Ast):
    _fields = ('arg', 'token')
    arg: str
    token: Token

    def __hash__(self):
        return hash(self.arg)


@dataclass
class Arguments(Ast):
    _fields = ('posonlyargs', 'args', 'vararg',
               'kwonlyargs', 'kw_defaults', 'kwarg', 'defaults')
    posonlyargs: list = field(default_factory=list)
    args: list = field(default_factory=list)
    vararg: Union[Arg, None] = None
    kwonlyargs: list = field(default_factory=list)
    kw_defaults: list = field(default_factory=list)
    kwarg: Union[Arg, None] = None
    defaults: list = field(default_factory=list)

    def __init__(self, posonlyargs=None, args=None, vararg=None,
                 kwonlyargs=None, kw_defaults=None, kwarg=None, defaults=None):
        self.posonlyargs = [] if posonlyargs is None else posonlyargs
        self.args = [] if args is None else args
        self.vararg = vararg
        self.kwonlyargs = [] if kwonlyargs is None else kwonlyargs
        self.kw_defaults = [] if kw_defaults is None else kw_defaults
        self.kwarg = kwarg
        self.defaults = [] if defaults is None else defaults

        argument_ids = {*()}

        for arg in self.posonlyargs + self.args + self.kwonlyargs:
            if arg in argument_ids:
                throw()

    def eval(self, /, *, env):
        return ArgumentsType(
            self.posonlyargs, self.args, self.vararg, self.kwonlyargs,
            self.kw_defaults, self.kwarg, self.defaults,
        )


@dataclass
class BuiltinFunction(Ast):
    _fields = ('args',)
    args: TypingTuple[Ast] = field(default_factory=list)


@dataclass
class Exit(BuiltinFunction, ScopeStmt):
    def eval(self, /, *, env):
        if len(self.args) > 1:
            throw(self.args[0].info, self.args[0].token, 'TypeError',
                  f'exit excepted at most 1 argument, got {len(self.args)}',
                  line=True)

        if self.args:
            print(self.args[0].eval(env=env))

        return self


@dataclass
class Input(BuiltinFunction):
    def eval(self, /, *, env):
        if len(self.args) > 1:
            throw(self.args[0].info, self.args[0].token, 'TypeError',
                  f'input excepted at most 1 argument, got {len(self.args)}',
                  line=True)

        return StringType(input() if not self.args
                          else input(self.args[0].eval(env=env)))


@dataclass
class Length(BuiltinFunction):
    def eval(self, /, *, env):
        if len(self.args) != 1:
            throw(self.args[0].info, self.args[0].token, 'TypeError',
                  f'length excepted exactly 1 arguments, got {len(self.args)}',
                  line=True)

        value = self.args[0].eval(env=env)

        if hasattr(value, '__len__'):
            return NumberType(len(value))
        else:
            throw(self.args[0].info, self.args[0].token, 'TypeError',
                  f'object of type {type(value).__name__} has no length()',
                  line=True)


@dataclass
class Match(BuiltinFunction):
    def eval(self, /, *, env):
        if len(self.args) != 2:
            throw(self.args[0].info, self.args[0].token, 'TypeError',
                  f'match excepted exactly 2 arguments, got {len(self.args)}',
                  line=True)

        pattern, string = self.args
        pattern_value = pattern.eval(env=env)
        string_value = string.eval(env=env)

        if not isinstance(pattern_value, StringType):
            throw(pattern.info, pattern.token, 'TypeError',
                  'the pattern must be a StringType', line=True)

        if not isinstance(string_value, StringType):
            throw(string.info, string.token, 'TypeError',
                  'the string must be a StringType', line=True)

        try:
            pattern_obj = re_compile(pattern_value.value)
        except re_error as err:
            throw(pattern.info, pattern.token, 'RegexError',
                  f'{err}', line=True)

        return bool(re_match(pattern_obj, string_value.value))


@dataclass
class Print(BuiltinFunction):
    def eval(self, /, *, env):
        print(' '.join(f'{value.eval(env=env)}' for value in self.args))
        return none


@dataclass
class Repr(BuiltinFunction):
    def eval(self, /, *, env):
        if len(self.args) > 1:
            throw(self.args[0].info, self.args[0].token, 'TypeError',
                  f'repr excepted at most 1 argument, got {len(self.args)}',
                  line=True)

        return StringType(f'{self.args[0].eval(env=env)!r}')


BUILTIN_FUNCTIONS = {
    'exit': Exit,
    'input': Input,
    'length': Length,
    'match': Match,
    'quit': Exit,
    'print': Print,
    'repr': Repr,
}
