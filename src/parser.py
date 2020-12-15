from rply import ParserGenerator

from .ast import (
    Module, Assign, AugAssign, Construct, Expr, Constant, Number, String, Name,
    BinOp, UnaryOp, Compare,
    Mult,
    Input, Print, Repr,
    If, While, Break, Continue, FunctionDef, Global, Nonlocal, Arguments, Arg,
    Load, Store,
)
from .error import throw
from .lexer import BIN_OP, INPLACE_OP, UNARY_OP, CMP_OP, TOKENS
from .obj import RESERVED, CONSTRUCTOR_TYPES


def informer(func, info):
    def output(*args, **kwargs):
        node = func(*args, **kwargs)
        node.info = info
        return node
    return output


class Parser:
    def __init__(self, /):
        self.pg = ParserGenerator(
            TOKENS,
            precedence=[
                ('left', ['NOT']),
                ('left', [
                    'LESS', 'LESSEQUAL',
                    'EQEQUAL', 'NOTEQUAL',
                    'GREATER', 'GREATEREQUAL', 'EQEQEQUAL', 'NOTEQEQEQUAL',
                    'IN', 'NOTIN',
                ]),
                ('left', ['VBAR']),
                ('left', ['CIRCUMFLEX']),
                ('left', ['AMPER']),
                ('left', ['PLUS', 'MINUS']),
                ('left', ['LEFTSHIFT', 'RIGHTSHIFT']),
                ('left', ['STAR', 'SLASH', 'DOUBLESLASH', 'PERCENT']),
                ('left', ['INVERT', 'UADD', 'USUB']),
                ('left', ['DOUBLESTAR']),
            ],
        )

    def add_syntaxes(self, info, /):
        @self.pg.production('program :')
        def empty_program(p):
            return Module()

        @self.pg.production('program : expr')
        def single_stmt_program(p):
            return Module([Expr(p[0])])

        @self.pg.production('program : expr SEMI program')
        def merge_expr_to_program(p):
            return Module([Expr(p[0]), *p[2].body])

        @self.pg.production('program : if_stmt program')
        @self.pg.production('program : if_else_stmt program')
        @self.pg.production('program : if_elif_stmt program')
        @self.pg.production('program : func_def program')
        @self.pg.production('program : while_stmt program')
        def merge_stmt_to_program(p):
            return Module([p[0], *p[1].body])

        @self.pg.production('program : break_stmt SEMI program')
        @self.pg.production('program : continue_stmt SEMI program')
        def merge_stmt_to_program(p):
            return Module([p[0], *p[2].body])

        @self.pg.production(
            'if_stmt : IF LPAR expr RPAR LBRACE program RBRACE'
        )
        def if_stmt(p):
            return If(p[2], p[5].body)

        @self.pg.production(
            'if_else_stmt : if_stmt or_else_stmt'
        )
        def if_else_stmt(p):
            return If(p[0].test, p[0].body, p[1])

        @self.pg.production(
            'if_elif_stmt : if_stmt merged_elif_stmt'
        )
        @self.pg.production(
            'if_elif_stmt : if_stmt elif_ending_stmt'
        )
        @self.pg.production(
            'if_elif_stmt : if_stmt elif_else_stmt'
        )
        def if_elif_stmt(p):
            return If(p[0].test, p[0].body, [p[1]])

        @self.pg.production(
            'merged_elif_stmt : elif_ending_stmt elif_ending_stmt'
        )
        @self.pg.production(
            'merged_elif_stmt : elif_ending_stmt elif_else_stmt'
        )
        @self.pg.production(
            'merged_elif_stmt : elif_ending_stmt merged_elif_stmt'
        )
        def merged_elif_stmt(p):
            return If(p[0].test, p[0].body, [p[1]])

        @self.pg.production(
            'elif_ending_stmt : ELIF LPAR expr RPAR LBRACE program RBRACE'
        )
        def elif_ending_stmt(p):
            return If(p[2].test, p[5].body)

        @self.pg.production(
            'elif_else_stmt : ELIF LPAR expr RPAR LBRACE program RBRACE'
            '                 or_else_stmt'
        )
        def elif_else_stmt(p):
            return If(p[2], p[5].body, p[7])

        @self.pg.production(
            'while_stmt : WHILE LPAR expr RPAR LBRACE program RBRACE'
        )
        def while_stmt(p):
            return While(p[2], p[5].body)

        @self.pg.production(
            'while_stmt : WHILE LPAR expr RPAR LBRACE program RBRACE'
            '             or_else_stmt'
        )
        def while_else_stmt(p):
            return While(p[2], p[5].body, p[7])

        @self.pg.production('or_else_stmt : ELSE LBRACE program RBRACE')
        def or_else_stmt(p):
            return p[2].body

        @self.pg.production('break_stmt : BREAK')
        def break_stmt(p):
            result = Break(p[0])
            result.info = info
            return result

        @self.pg.production('continue_stmt : CONTINUE')
        def continue_stmt(p):
            result = Continue(p[0])
            result.info = info
            return result

        @self.pg.production(
            'func_def : FUNC NAME LPAR args_def RPAR'
            '           LBRACE program RBRACE'
        )
        def func_def_stmt(p):
            return FunctionDef(p[1].value, p[3], p[6].body)

        @self.pg.production('args_def :')
        def empty_args_def_expr(p):
            return Arguments()

        @self.pg.production('args_def : pos_only_args')
        @self.pg.production('args_def : normal_args')
        @self.pg.production('args_def : kw_only_args')
        def single_type_args_def_expr(p):
            return p[0]

        @self.pg.production('args_def : pos_only_args COMMA normal_args')
        def poa_na_args_def_expr(p):
            return Arguments(
                posonlyargs=p[0].posonlyargs, args=p[2].args,
                defaults=p[0].defaults + p[2].defaults,
            )

        @self.pg.production(
            'args_def : pos_only_args COMMA kw_only_args opt_kwarg'
        )
        def poa_koa_args_def_expr(p):
            return Arguments(
                posonlyargs=p[0].posonlyargs, vararg=p[2].vararg,
                kwonlyargs=p[2].kwonlyargs, defaults=p[0].defaults,
                kw_defaults=p[2].kw_defaults, kwarg=p[3].kwarg,
            )

        @self.pg.production(
            'args_def : normal_args COMMA kw_only_args opt_kwarg'
        )
        def na_koa_args_def_expr(p):
            return Arguments(
                args=p[0].args, vararg=p[2].vararg, kwonlyargs=p[2].kwonlyargs,
                defaults=p[0].defaults, kw_defaults=p[2].kw_defaults,
                kwarg=p[3].kwarg,
            )

        @self.pg.production(
            'args_def : pos_only_args COMMA normal_args COMMA kw_only_args'
            '           opt_kwarg'
        )
        def poa_na_koa_args_def_expr(p):
            return Arguments(
                posonlyargs=p[0].posonlyargs, args=p[2].args,
                vararg=p[4].vararg, kwonlyargs=p[4].kwonlyargs,
                defaults=p[0].defaults + p[2].defaults,
                kw_defaults=p[4].kw_defaults, kwarg=p[5].kwarg,
            )

        @self.pg.production('kw_only_args : STAR')
        def empty_kw_only_args_expr(p):
            return Arguments()

        @self.pg.production('kw_only_args : STAR COMMA args')
        @self.pg.production('kw_only_args : STAR COMMA kwargs')
        def kw_only_args_expr(p):
            return Arguments(kwonlyargs=p[2][0], kw_defaults=p[2][1])

        @self.pg.production('kw_only_args : STAR COMMA args COMMA kwargs')
        def kw_only_args_kwargs_expr(p):
            return Arguments(
                kwonlyargs=p[2][0] + p[4][0],
                kw_defaults=p[2][1] + p[4][1],
            )

        @self.pg.production('kw_only_args : STAR NAME COMMA args')
        @self.pg.production('kw_only_args : STAR NAME COMMA kwargs')
        def kw_only_args_with_vararg_expr(p):
            return Arguments(
                vararg=Arg(p[1].value), kwonlyargs=p[3][0], kw_defaults=p[3][1]
            )

        @self.pg.production('kw_only_args : STAR NAME COMMA args COMMA kwargs')
        def kw_only_args_with_vararg_kwargs_expr(p):
            return Arguments(
                vararg=Arg(p[1].value),
                kwonlyargs=p[3][0] + p[5][0], kw_defaults=p[3][1] + p[5][1],
            )

        @self.pg.production('opt_kwarg :')
        def empty_optional_keyword_arg_expr(p):
            return Arguments(kwarg=None)

        @self.pg.production('opt_kwarg : DOUBLESTAR NAME')
        def optional_keyword_arg_expr(p):
            return Arguments(kwarg=Arg(p[1].value))

        @self.pg.production('normal_args :')
        def empty_normal_args_expr(p):
            return Arguments()

        @self.pg.production('normal_args : args')
        @self.pg.production('normal_args : kwargs')
        def normal_args_expr(p):
            return Arguments(args=p[0][0], defaults=p[0][1])

        @self.pg.production('normal_args : args COMMA kwargs')
        def normal_args_kwargs_expr(p):
            return Arguments(
                args=p[0][0] + p[2][0], defaults=p[0][1] + p[2][1]
            )

        @self.pg.production('pos_only_args : SLASH')
        def empty_pos_only_args_expr(p):
            return Arguments()

        @self.pg.production('pos_only_args : args COMMA SLASH')
        @self.pg.production('pos_only_args : kwargs COMMA SLASH')
        def pos_only_args_expr(p):
            return Arguments(posonlyargs=p[0][0], defaults=p[0][1])

        @self.pg.production('pos_only_args : args COMMA kwargs COMMA SLASH')
        def pos_only_args_kwargs_expr(p):
            return Arguments(
                posonlyargs=p[0][0] + p[2][0], defaults=p[0][1] + p[2][1]
            )

        @self.pg.production('args : NAME COMMA args')
        def args_expr(p):
            return [[Arg(p[0].value), *p[2][0]], [None, *p[2][1]]]

        @self.pg.production('args : NAME')
        def single_arg_expr(p):
            return [[Arg(p[0].value)], [None]]

        @self.pg.production('kwargs : NAME EQUAL expr COMMA kwargs')
        def keyword_args_expr(p):
            return [[Arg(p[0].value), *p[4][0]], [p[2], *p[4][1]]]

        @self.pg.production('kwargs : NAME EQUAL expr')
        def single_keyword_arg_expr(p):
            return [[Arg(p[0].value)], [p[2]]]

        @self.pg.production('expr : NAME EQUAL expr')
        def assignment_expr(p):
            if p[0].value in RESERVED:
                throw(info, p[0], 'SyntaxError',
                      f'cannot assign to {p[0].value}')
            name = Name(p[0], Store())
            name.info = info
            return Assign(name, p[2])

        @self.pg.production('expr : LPAR expr RPAR')
        def expr_with_parentheses(p):
            return p[1]

        @self.pg.production('expr : NUMBER LPAR expr RPAR')
        def parentheses_number_multiplication(p):
            return BinOp(Number(p[0]), Mult, p[2])

        @self.pg.production('expr : NAME LPAR RPAR')
        @self.pg.production('expr : NAME LPAR expr RPAR')
        def function_expr(p):
            if len(p) == 3:
                args = ()
            elif len(p) == 4:
                args = (p[2],)

            if p[0].value == 'input':
                return Input(*args)
            elif p[0].value == 'print':
                return Print(*args)
            elif p[0].value == 'repr':
                return Repr(*args)

            elif p[0].value in CONSTRUCTOR_TYPES:
                if len(p) == 3:
                    return Construct(CONSTRUCTOR_TYPES[p[0].value])
                elif len(p) == 4:
                    value = p[2]
                    value.info = info
                    return Construct(CONSTRUCTOR_TYPES[p[0].value], value)

        @self.pg.production('expr : expr PLUS expr')
        @self.pg.production('expr : expr MINUS expr')
        @self.pg.production('expr : expr STAR expr')
        @self.pg.production('expr : expr SLASH expr')
        @self.pg.production('expr : expr DOUBLESLASH expr')
        @self.pg.production('expr : expr PERCENT expr')
        @self.pg.production('expr : expr DOUBLESTAR expr')
        @self.pg.production('expr : expr LEFTSHIFT expr')
        @self.pg.production('expr : expr RIGHTSHIFT expr')
        @self.pg.production('expr : expr AMPER expr')
        @self.pg.production('expr : expr CIRCUMFLEX expr')
        @self.pg.production('expr : expr VBAR expr')
        def binop_expr(p):
            left, op, right = p
            bin_op = BIN_OP[op.gettokentype()]()
            bin_op.info = info
            left.info = info
            right.info = info
            return BinOp(left, bin_op, right)

        @self.pg.production('expr : NAME PLUSEQUAL expr')
        @self.pg.production('expr : NAME MINUSEQUAL expr')
        @self.pg.production('expr : NAME STAREQUAL expr')
        @self.pg.production('expr : NAME SLASHEQUAL expr')
        @self.pg.production('expr : NAME DOUBLESLASHEQUAL expr')
        @self.pg.production('expr : NAME PERCENTEQUAL expr')
        @self.pg.production('expr : NAME DOUBLESTAREQUAL expr')
        @self.pg.production('expr : NAME LEFTSHIFTEQUAL expr')
        @self.pg.production('expr : NAME RIGHTSHIFTEQUAL expr')
        @self.pg.production('expr : NAME AMPEREQUAL expr')
        @self.pg.production('expr : NAME CIRCUMFLEXEQUAL expr')
        @self.pg.production('expr : NAME VBAREQUAL expr')
        def inplace_assign_expr(p):
            name, op, value = p
            if name.value in RESERVED:
                throw(info, name, 'SyntaxError',
                      f"'{name.value}' is an illegal expression "
                      f"for augmented assignment")

            name = Name(name, Store())
            name.info = info
            bin_op = INPLACE_OP[op.gettokentype()]()
            bin_op.info = info
            value.info = info
            return AugAssign(name, bin_op, value)

        @self.pg.production('expr : NUMBER NAME')
        def variable_multiplication(p):
            if p[1].value in RESERVED:
                name = Constant(p[1])
            else:
                name = Name(p[1], Load())
            name.info = info
            return BinOp(Number(p[0]), Mult, name)

        @self.pg.production('expr : TILDE expr', precedence='INVERT')
        @self.pg.production('expr : NOT expr')
        @self.pg.production('expr : PLUS expr', precedence='UADD')
        @self.pg.production('expr : MINUS expr', precedence='USUB')
        def unaryop_expr(p):
            op, operand = p
            unary_op = UNARY_OP[op.gettokentype()]()
            unary_op.info = info
            operand.info = info
            return UnaryOp(unary_op, operand)

        @self.pg.production('expr : cmp_expr')
        def cmp_expr_escape(p):
            return p[0]

        @self.pg.production('cmp_expr : expr LESS expr')
        @self.pg.production('cmp_expr : expr LESSEQUAL expr')
        @self.pg.production('cmp_expr : expr EQEQUAL expr')
        @self.pg.production('cmp_expr : expr NOTEQUAL expr')
        @self.pg.production('cmp_expr : expr GREATER expr')
        @self.pg.production('cmp_expr : expr GREATEREQUAL expr')
        @self.pg.production('cmp_expr : expr EQEQEQUAL expr')
        @self.pg.production('cmp_expr : expr NOTEQEQEQUAL expr')
        @self.pg.production('cmp_expr : expr IN expr')
        @self.pg.production('cmp_expr : cmp_expr LESS expr')
        @self.pg.production('cmp_expr : cmp_expr LESSEQUAL expr')
        @self.pg.production('cmp_expr : cmp_expr EQEQUAL expr')
        @self.pg.production('cmp_expr : cmp_expr NOTEQUAL expr')
        @self.pg.production('cmp_expr : cmp_expr GREATER expr')
        @self.pg.production('cmp_expr : cmp_expr GREATEREQUAL expr')
        @self.pg.production('cmp_expr : cmp_expr EQEQEQUAL expr')
        @self.pg.production('cmp_expr : cmp_expr NOTEQEQEQUAL expr')
        @self.pg.production('cmp_expr : cmp_expr IN expr')
        def cmp_expr(p):
            left, op, right = p
            cmp_op = CMP_OP[op.gettokentype()]()
            cmp_op.info = info
            left.info = info
            right.info = info
            if isinstance(left, Compare):
                return Compare(
                    left, left.ops + [cmp_op], left.comparators + [right]
                )
            else:
                return Compare(left, [cmp_op], [right])

        @self.pg.production('cmp_expr : expr NOT IN expr',
                            precedence='NOTIN')
        @self.pg.production('cmp_expr : cmp_expr NOT IN expr',
                            precedence='NOTIN')
        def multi_cmp_expr(p):
            left, *ops, right = p
            cmp_op = CMP_OP[tuple(op.gettokentype() for op in ops)]
            cmp_op.info = info
            left.info = info
            right.info = info
            if isinstance(left, Compare):
                return Compare(
                    left, left.ops + [cmp_op], left.comparators + [right]
                )
            else:
                return Compare(left, [cmp_op], [right])

        @self.pg.production('expr : NAME')
        def constant(p):
            if p[0].value in RESERVED:
                return Constant(p[0])
            name = Name(p[0], Load())
            name.info = info
            return name

        @self.pg.production('expr : NUMBER')
        def number(p):
            return Number(p[0])

        @self.pg.production('expr : STRING')
        def string(p):
            return String(p[0])

        for name in dir():
            if name == 'self':
                continue
            locals()[name] = informer(locals()[name], info)

        @self.pg.error
        def error_handle(token):
            throw(info, token, 'SyntaxError', 'invalid syntax')

    def get_parser(self, /, *, info):
        self.add_syntaxes(info)
        return self.pg.build()


def get_parser(*, info):
    return Parser().get_parser(info=info)
