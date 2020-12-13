from copy import deepcopy

from rply.token import BaseBox, Token

from .error import throw
from .obj import (
    Type,
    ModuleType, BooleanType, NoneType, NumberType, StringType, NameType,
    FunctionType, ArgumentsType, ArgType,
    RESERVED, DEFAULT_ENV,
)


class Ast(BaseBox):
    info = None


class Module(Ast):
    def __init__(self, body=None):
        self.body = [] if body is None else body

    def eval(self):
        env = deepcopy(DEFAULT_ENV)

        for stmt in self.body:
            if isinstance(stmt, ScopeStmt):
                throw(stmt.info, stmt.token, 'SyntaxError',
                      f"cannot use '{type(stmt).__name__.lower()}'"
                      f" outside loop")
            stmt.eval(env)

        return ModuleType(env)


class Assign(Ast):
    def __init__(self, target, value):
        self.target = target
        self.value = value

    def eval(self, env):
        value = self.value.eval(env)
        env[self.target.eval(env).id] = value
        return value


class AugAssign(Ast):
    def __init__(self, target, op, value):
        self.target = target
        self.op = op
        self.value = value

    def eval(self, env):
        value = self.op.eval(env[self.target.eval(env).id], self.value, env)
        env[self.target.eval(env).id] = value
        return value


class Expr(Ast):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value.eval(env)


class Constant(Ast):
    def __init__(self, token):
        self.token = token

    def eval(self, env):
        return RESERVED[self.token.value]


class Number(Ast):
    def __init__(self, token):
        self.token = token

    def eval(self, env):
        return NumberType(float(self.token.value))


class String(Ast):
    def __init__(self, token):
        self.token = token

    def eval(self, env):
        return StringType(eval(self.token.value))


class ExprFunc(Ast):
    pass


class Load(ExprFunc):
    pass


class Store(ExprFunc):
    pass


class Name(Ast):
    def __init__(self, token, ctx):
        self.token = token
        self.id = token.value
        self.ctx = ctx

    def eval(self, env):
        if isinstance(self.ctx, Load):
            if self.id not in env:
                throw(self.info, self.token, 'NameError',
                      f"name '{self.id}' is not found")
            return env[self.id]
        else:
            return NameType(self.id)


class BinOp(Ast):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def eval(self, env):
        return self.op.eval(self.left, self.right, env)


class Operator(Ast):
    @staticmethod
    def process(value, env):
        if isinstance(value, Ast):
            return value.eval(env)
        else:
            return value


class Add(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__add__'):
            result = left_value.__add__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__radd__'):
            result = right_value.__radd__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for +: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class Sub(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__sub__'):
            result = left_value.__sub__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rsub__'):
            result = right_value.__rsub__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for -: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class Mult(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__mul__'):
            result = left_value.__mul__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rmul__'):
            result = right_value.__rmul__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for *: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class Div(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__truediv__'):
            result = left_value.__truediv__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rtruediv__'):
            result = right_value.__rtruediv__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for /: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class FloorDiv(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__floordiv__'):
            result = left_value.__floordiv__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rfloordiv__'):
            result = right_value.__rfloordiv__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for //: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class Mod(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__mod__'):
            result = left_value.__mod__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rmod__'):
            result = right_value.__rmod__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for %: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class Pow(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__pow__'):
            result = left_value.__pow__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rpow__'):
            result = right_value.__rpow__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for **: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class LShift(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__lshift__'):
            result = left_value.__lshift__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rlshift__'):
            result = right_value.__rlshift__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for <<: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class RShift(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__rshift__'):
            result = left_value.__rshift__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rrshift__'):
            result = right_value.__rrshift__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for >>: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class BitAnd(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__and__'):
            result = left_value.__and__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rand__'):
            result = right_value.__rand__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for &: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class BitXor(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__xor__'):
            result = left_value.__xor__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__rxor__'):
            result = right_value.__rxor__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for ^: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class BitOr(Operator):
    @classmethod
    def eval(cls, left, right, env):
        left_value = cls.process(left, env)
        right_value = cls.process(right, env)

        if hasattr(left_value, '__or__'):
            result = left_value.__or__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__ror__'):
            result = right_value.__ror__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result
        else:
            throw(left.info, left.token, 'TypeError',
                  f"unsupported operand type(s) for |: "
                  f"'{type(left_value).__name__}' and "
                  f"'{type(right_value).__name__}'", line=True)


class UnaryOp(Ast):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def eval(self, env):
        return self.op.eval(self.operand, env)


class UnaryOperator(Ast):
    pass


class Invert(UnaryOperator):
    @staticmethod
    def eval(operand, env):
        operand_value = operand.eval(env)

        if hasattr(operand_value, '__invert__'):
            return operand_value.__invert__()
        else:
            throw(operand.info, operand.token, 'TypeError',
                  f"bad operand type for unary ~: "
                  f"'{type(operand_value).__name__}'", line=True)


class Not(UnaryOperator):
    @staticmethod
    def eval(operand, env):
        operand_value = operand.eval(env)

        if hasattr(operand_value, '__bool__'):
            return ~BooleanType(operand_value)
        else:
            return BooleanType(False)


class UAdd(UnaryOperator):
    @staticmethod
    def eval(operand, env):
        operand_value = operand.eval(env)

        if hasattr(operand_value, '__pos__'):
            return operand_value.__pos__()
        else:
            throw(left.info, left.token, 'TypeError',
                  f"bad operand type for unary +: "
                  f"'{type(left_value).__name__}'", line=True)


class USub(UnaryOperator):
    @staticmethod
    def eval(operand, env):
        operand_value = operand.eval(env)

        if hasattr(operand_value, '__neg__'):
            return operand_value.__neg__()
        else:
            throw(left.info, left.token, 'TypeError',
                  f"bad operand type for unary -: "
                  f"'{type(left_value).__name__}'", line=True)


class Compare(Ast):
    def __init__(self, left, ops, comparators):
        self.left = left
        self.ops = ops
        self.comparators = comparators

    def eval(self, env):
        last = self.left
        for index in range(len(self.ops)):
            if not self.ops[index].eval(
                last, self.comparators[index], env
            ):
                return BooleanType(False)
            last = self.comparators[index]

        return BooleanType(True)


class CmpOp(Ast):
    pass


class Eq(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__eq__'):
            result = left_value.__eq__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__eq__'):
            result = right_value.__eq__(left_value)
        else:
            result = NotImplemented

        if hasattr(left_value, '__ne__'):
            result = left_value.__ne__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result

        if hasattr(right_value, '__ne_'):
            result = right_value.__ne__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result
        else:
            return BooleanType(False)


class Gt(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__gt__'):
            result = left_value.__gt__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__le__'):
            result = right_value.__le__(left_value)
        else:
            result = NotImplemented

        if hasattr(left_value, '__le__'):
            result = left_value.__le__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result

        if hasattr(right_value, '__gt_'):
            result = right_value.__gt__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result
        else:
            return BooleanType(False)


class GtE(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__ge__'):
            result = left_value.__ge__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__lt__'):
            result = right_value.__lt__(left_value)
        else:
            result = NotImplemented

        if hasattr(left_value, '__lt__'):
            result = left_value.__lt__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result

        if hasattr(right_value, '__ge_'):
            result = right_value.__ge__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result
        else:
            return BooleanType(False)


class In(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__contains__'):
            return left_value.__contains__(right_value)
        else:
            return BooleanType(False)


class Is(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        return BooleanType(left_value is right_value)


class IsNot(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        return BooleanType(left_value is not right_value)


class Lt(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__lt__'):
            result = left_value.__lt__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__ge__'):
            result = right_value.__ge__(left_value)
        else:
            result = NotImplemented

        if hasattr(left_value, '__ge__'):
            result = left_value.__ge__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result

        if hasattr(right_value, '__lt_'):
            result = right_value.__lt__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result
        else:
            return BooleanType(False)


class LtE(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__le__'):
            result = left_value.__le__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__gt__'):
            result = right_value.__gt__(left_value)
        else:
            result = NotImplemented

        if hasattr(left_value, '__gt__'):
            result = left_value.__gt__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result

        if hasattr(right_value, '__le__'):
            result = right_value.__le__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result
        else:
            return BooleanType(False)


class NotEq(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__ne__'):
            result = left_value.__ne__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return result

        if hasattr(right_value, '__ne__'):
            result = right_value.__ne__(left_value)
        else:
            result = NotImplemented

        if hasattr(left_value, '__eq__'):
            result = left_value.__eq__(right_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result

        if hasattr(right_value, '__eq__'):
            result = right_value.__eq__(left_value)
        else:
            result = NotImplemented

        if result is not NotImplemented:
            return ~result
        else:
            return BooleanType(False)


class NotIn(CmpOp):
    @staticmethod
    def eval(left, right, env):
        left_value = left.eval(env)
        right_value = right.eval(env)

        if hasattr(left_value, '__contains__'):
            return ~left_value.__contains__(right_value)
        else:
            return BooleanType(False)


class If(Ast):
    def __init__(self, test, body, orelse=None):
        self.test = test
        self.body = body
        self.orelse = [] if orelse is None else orelse

    def eval(self, env):
        for stmt in self.body if self.test.eval(env) else self.orelse:
            if isinstance(stmt, ScopeStmt):
                return stmt

            result = stmt.eval(env)
            if isinstance(result, ScopeStmt):
                return result


class While(Ast):
    def __init__(self, test, body, orelse=None):
        self.test = test
        self.body = body
        self.orelse = [] if orelse is None else orelse

    def eval(self, env):
        run_orelse = True

        while self.test.eval(env):
            for stmt in self.body:
                if isinstance(stmt, Break):
                    return
                elif isinstance(stmt, Continue):
                    break

                result = stmt.eval(env)
                if isinstance(result, Break):
                    return
                elif isinstance(result, Continue):
                    break

        for stmt in self.orelse:
            if isinstance(stmt, ScopeStmt):
                return stmt

            result = stmt.eval(env)
            if isinstance(result, ScopeStmt):
                return result


class ScopeStmt(Ast):
    def __init__(self, token):
        self.token = token

    def eval(self, env):
        pass


class Break(ScopeStmt):
    pass


class Continue(ScopeStmt):
    pass


class FunctionDef(Ast):
    def __init__(self, name, args=None, body=None):
        self.name = name
        self.args = Arguments() if args is None else args
        self.body = [] if body is None else body

    def eval(self, env):
        env[self.name] = FunctionType(self.name, self.args, self.body)


class Global(Ast):
    def __init__(self, names):
        self.names = names

    def eval(self, env):
        pass


class Return(Ast):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        pass


class Nonlocal(Ast):
    def __init__(self, names):
        self.names = names

    def eval(self, env):
        pass


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

class Arg(Ast):
    def __init__(self, arg):
        self.arg = arg


class Arguments(Ast):
    def __init__(self, posonlyargs=None, args=None, vararg=None,
                 kwonlyargs=None, kw_defaults=None, kwarg=None, defaults=None):
        self.posonlyargs = [] if posonlyargs is None else posonlyargs
        self.args = [] if args is None else args
        self.vararg = vararg
        self.kwonlyargs = [] if kwonlyargs is None else kwonlyargs
        self.kw_defaults = [] if kw_defaults is None else kw_defaults
        self.kwarg = kwarg
        self.defaults = [] if defaults is None else defaults

    def eval(self, env):
        return ArgumentsType(
            self.posonlyargs, self.args, self.vararg, self.kwonlyargs,
            self.kw_defaults, self.kwarg, self.defaults,
        )


class Input(Ast):
    def __init__(self, prompt=None):
        self.prompt = prompt

    def eval(self, env):
        output = (input() if self.prompt is None
                  else input(self.prompt.eval(env)))
        return StringType(output)


class Print(Ast):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        print(self.value.eval(env))
        return NoneType()


class Repr(Ast):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return StringType(f'{self.value.eval(env)!r}')
