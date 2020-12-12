from rply import ParserGenerator

from .ast import (
    Module, Assign, Expr, Constant, Number, String, Name,
    BinOp, UnaryOp, Compare,
    Mult,
    Input, Print, Repr,
    If,
    Load, Store,
)
from .error import throw
from .lexer import BIN_OP, UNARY_OP, CMP_OP, TOKENS
from .obj import RESERVED


def informer(func, info):
    def output(*args, **kwargs):
        node = func(*args, **kwargs)
        node.info = info
        return node
    return output


class Parser():
    def __init__(self):
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
                ('left', ['PLUS', 'MINUS']),
                ('left', ['STAR', 'SLASH', 'DOUBLESLASH', 'PERCENT']),
                ('left', ['INVERT', 'UADD', 'USUB']),
                ('left', ['DOUBLESTAR']),
            ],
        )

    def parse(self, info):
        @self.pg.production('program :')
        def empty_program(p):
            return Module()

        @self.pg.production('program : expr')
        def single_stmt_program(p):
            return Module([Expr(p[0])])

        @self.pg.production('program : if_stmt')
        @self.pg.production('program : if_else_stmt')
        @self.pg.production('program : if_elif_stmt')
        def merge_program(p):
            return Module([p[0]])

        @self.pg.production('program : expr SEMI program')
        def merge_program(p):
            return Module([Expr(p[0]), *p[2].body])

        @self.pg.production('program : if_stmt program')
        @self.pg.production('program : if_else_stmt program')
        @self.pg.production('program : if_elif_stmt program')
        def merge_program(p):
            return Module([p[0], *p[1].body])

        @self.pg.production(
            'if_stmt : IF LPAR expr RPAR LBRACE program RBRACE'
        )
        def if_stmt(p):
            return If(p[2], p[5].body)

        @self.pg.production(
            'if_else_stmt : if_stmt ELSE LBRACE program RBRACE'
        )
        def if_else_stmt(p):
            return If(p[0].test, p[0].body, p[3].body)

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
            '                 ELSE LBRACE program RBRACE'
        )
        def elif_else_stmt(p):
            return If(p[2], p[5].body, p[9].body)

        @self.pg.production('expr : NAME EQUAL expr')
        def assignment_expr(p):
            if p[0].value in RESERVED:
                exit(f'cannot assign to {p[0].value}')
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

        @self.pg.production('expr : expr PLUS expr')
        @self.pg.production('expr : expr MINUS expr')
        @self.pg.production('expr : expr STAR expr')
        @self.pg.production('expr : expr SLASH expr')
        @self.pg.production('expr : expr DOUBLESLASH expr')
        @self.pg.production('expr : expr PERCENT expr')
        @self.pg.production('expr : expr DOUBLESTAR expr')
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

    def get_parser(self):
        return self.pg.build()
