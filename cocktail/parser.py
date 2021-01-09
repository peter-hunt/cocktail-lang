from re import match
from warnings import catch_warnings, filterwarnings

from .rply.errors import LexingError, ParserGeneratorWarning
from .rply.parser import LRParser
from .rply.parsergenerator import ParserGenerator

from .ast import *
from .error import throw
from .lexer import (
    lex,
    BIN_OP, INPLACE_OP, UNARY_OP, CMP_OP,
    POST_INPLACE_UNARY_OP, PRE_INPLACE_UNARY_OP,
    TOKENS,
)
from .moduleinfo import ModuleInfo
from .obj import (
    RESERVED, CONSTRUCTOR_TYPES,
    none,
)


__all__ = ['Parser', 'get_parser', 'parse']


class Parser:
    def __init__(self, /) -> None:
        self.pg = ParserGenerator(
            TOKENS,
            precedence=[
                ('left', ['EQUAL', *INPLACE_OP]),
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
                ('right', ['INVERT', 'UADD', 'USUB']),
                ('left', ['DOUBLESTAR']),
            ],
        )

    def add_syntaxes(self, info: ModuleInfo, /) -> None:
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
        @self.pg.production('program : for_stmt program')
        @self.pg.production('program : for_of_stmt program')
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

        @self.pg.production('if_else_stmt : if_stmt or_else_stmt')
        def if_else_stmt(p):
            return If(p[0].test, p[0].body, p[1])

        @self.pg.production('if_elif_stmt : if_stmt merged_elif_stmt')
        @self.pg.production('if_elif_stmt : if_stmt elif_ending_stmt')
        @self.pg.production('if_elif_stmt : if_stmt elif_else_stmt')
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
            'for_stmt : FOR LPAR opt_expr SEMI opt_expr SEMI opt_expr RPAR'
            '           LBRACE program RBRACE'
        )
        def for_stmt(p):
            return For(p[2], p[4], p[6], p[9].body)

        @self.pg.production(
            'for_stmt : FOR LPAR opt_expr SEMI opt_expr SEMI opt_expr RPAR'
            '           LBRACE program RBRACE or_else_stmt'
        )
        def for_stmt(p):
            return For(p[2], p[4], p[6], p[9].body, p[11])

        @self.pg.production(
            'for_of_stmt : FOR LPAR NAME OF expr RPAR LBRACE program RBRACE'
        )
        def for_of_stmt(p):
            return ForOf(Name(p[2], Store()), p[4], p[7].body)

        @self.pg.production(
            'for_of_stmt : FOR LPAR NAME OF expr RPAR LBRACE program RBRACE'
            '              or_else_stmt'
        )
        def for_of_stmt(p):
            return ForOf(Name(p[2], Store()), p[4], p[7].body, p[9])

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
            return Break(p[0])

        @self.pg.production('continue_stmt : CONTINUE')
        def continue_stmt(p):
            result = Continue(p[0])
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
                vararg=Arg(p[1].value, p[1]),
                kwonlyargs=p[3][0], kw_defaults=p[3][1]
            )

        @self.pg.production('kw_only_args : STAR NAME COMMA args COMMA kwargs')
        def kw_only_args_with_vararg_kwargs_expr(p):
            return Arguments(
                vararg=Arg(p[1].value, p[1]),
                kwonlyargs=p[3][0] + p[5][0], kw_defaults=p[3][1] + p[5][1],
            )

        @self.pg.production('opt_kwarg :')
        def empty_optional_keyword_arg_expr(p):
            return Arguments(kwarg=None)

        @self.pg.production('opt_kwarg : DOUBLESTAR NAME')
        def optional_keyword_arg_expr(p):
            return Arguments(kwarg=Arg(p[1].value, p[1]))

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
            return [[Arg(p[0].value, p[0]), *p[2][0]], [None, *p[2][1]]]

        @self.pg.production('args : NAME')
        def single_arg_expr(p):
            return [[Arg(p[0].value, p[0])], [None]]

        @self.pg.production('kwargs : assignment COMMA kwargs')
        def keyword_args_expr(p):
            return [[Arg(p[0].target.id, p[0].target.token), *p[4][0]],
                    [p[0].value, *p[4][1]]]

        @self.pg.production('kwargs : assignment')
        def single_keyword_arg_expr(p):
            return [[Arg(p[0].target.id, p[0].target.token)],
                    [p[0].value]]

        @self.pg.production('expr : assignment')
        def assignment_as_expr(p):
            return p[0]

        @self.pg.production('assignment : NAME EQUAL expr')
        def assignment(p):
            if p[0].value in RESERVED:
                throw(info, p[0], 'SyntaxError',
                      f'cannot assign to {p[0].value}')
            name = Name(p[0], Store())
            return Assign(name, p[2])

        @self.pg.production('expr : LPAR expr RPAR')
        def expr_with_parentheses(p):
            return p[1]

        @self.pg.production('expr : NUMBER LPAR expr RPAR')
        def parentheses_number_multiplication(p):
            return BinOp(Number(p[0]), Mult, p[2])

        @self.pg.production('expr : expr LPAR RPAR')
        @self.pg.production('expr : expr LPAR tuple_expr RPAR')
        @self.pg.production('expr : expr LPAR tuple_expr COMMA RPAR')
        def function_call_expr(p):
            args = () if len(p) == 3 else p[2].values

            if isinstance(p[0], Name):
                if p[0].token.value in BUILTIN_FUNCTIONS:
                    return BUILTIN_FUNCTIONS[p[0].token.value](args)

                elif p[0].token.value in CONSTRUCTOR_TYPES:
                    return Construct(CONSTRUCTOR_TYPES[p[0].token.value], args)

            else:
                return Call(p[0], args, {})

        @self.pg.production('expr : expr LSQB expr RSQB')
        def get_item_expr(p):
            return GetItem(p[0], p[2])

        @self.pg.production('expr : expr LSQB opt_expr COLON opt_expr RSQB')
        @self.pg.production('expr : expr '
                            'LSQB opt_expr COLON opt_expr COLON opt_expr RSQB')
        def get_item_expr(p):
            return GetItem(
                p[0], Slice(p[2], p[4], none if len(p) == 6 else p[6])
            )

        @self.pg.production('opt_expr : ')
        @self.pg.production('opt_expr : expr')
        def optional_expr(p):
            return p[0] if p else Constant(none)

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
            return BinOp(p[0], BIN_OP[p[1].gettokentype()](), p[2])

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
            if p[0].value in RESERVED:
                throw(info, p[0], 'SyntaxError',
                      f"'{p[0].value}' is an illegal expression "
                      f"for augmented assignment")

            return AugAssign(
                Name(p[0], Store()),
                INPLACE_OP[p[1].gettokentype()](),
                p[2],
            )

        @self.pg.production('expr : NAME PLUSPLUS')
        @self.pg.production('expr : NAME MINUSMINUS')
        def inplace_unary_expr(p):
            if p[0].value in RESERVED:
                throw(info, p[0], 'SyntaxError',
                      f"'{p[0].value}' is an illegal expression "
                      f"for inplace unary operation")

            return InplaceUnaryOp(
                Name(p[0], Load()),
                Name(p[0], Store()),
                POST_INPLACE_UNARY_OP[p[1].gettokentype()](),
            )

        @self.pg.production('expr : PLUSPLUS NAME')
        @self.pg.production('expr : MINUSMINUS NAME')
        def inplace_unary_expr(p):
            if p[1].value in RESERVED:
                throw(info, p[0], 'SyntaxError',
                      f"'{p[0].value}' is an illegal expression "
                      f"for inplace unary operation")

            return InplaceUnaryOp(
                Name(p[1], Load()),
                Name(p[1], Store()),
                PRE_INPLACE_UNARY_OP[p[0].gettokentype()](),
            )

        @self.pg.production('expr : NUMBER NAME')
        def variable_multiplication(p):
            return BinOp(
                Number(p[0]), Mult,
                Constant(p[1]) if p[1].value in RESERVED
                else Name(p[1], Load()),
            )

        @self.pg.production('expr : TILDE expr', precedence='INVERT')
        @self.pg.production('expr : NOT expr')
        @self.pg.production('expr : PLUS expr', precedence='UADD')
        @self.pg.production('expr : MINUS expr', precedence='USUB')
        def unaryop_expr(p):
            return UnaryOp(UNARY_OP[p[0].gettokentype()](), p[1])

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
            left = p[0]
            cmp_op = CMP_OP[p[1].gettokentype()]()
            if isinstance(left, Compare):
                return Compare(
                    left, left.ops + [cmp_op], left.comparators + [p[2]]
                )
            else:
                return Compare(left, [cmp_op], [p[2]])

        @self.pg.production('cmp_expr : expr NOT IN expr',
                            precedence='NOTIN')
        @self.pg.production('cmp_expr : cmp_expr NOT IN expr',
                            precedence='NOTIN')
        def multi_cmp_expr(p):
            left = p[0]
            cmp_op = CMP_OP[tuple(op.gettokentype() for op in p[1:-1])]
            if isinstance(p[0], Compare):
                return Compare(
                    left, left.ops + [cmp_op], left.comparators + [p[-1]]
                )
            else:
                return Compare(left, [cmp_op], [p[-1]])

        @self.pg.production('expr : NAME')
        def constant(p):
            if p[0].value in RESERVED:
                return Constant(p[0])
            return Name(p[0], Load())

        @self.pg.production('expr : NUMBER')
        def number(p):
            return Number(p[0])

        @self.pg.production('expr : STRING')
        def string(p):
            return String(p[0])

        @self.pg.production('expr : LPAR RPAR')
        def empty_tuple(p):
            return Tuple(())

        @self.pg.production('expr : LPAR tuple_expr RPAR')
        @self.pg.production('expr : LPAR tuple_expr COMMA RPAR')
        def filled_tuple(p):
            return p[1]

        @self.pg.production('expr : LSQB RSQB')
        def empty_list(p):
            return List([])

        @self.pg.production('expr : LSQB tuple_expr RSQB')
        @self.pg.production('expr : LSQB tuple_expr COMMA RSQB')
        def filled_list(p):
            return List([*p[1].values])

        @self.pg.production('tuple_expr : expr')
        def single_tuple_expr(p):
            return Tuple((p[0],))

        @self.pg.production('tuple_expr : tuple_expr COMMA expr')
        def multiple_tuple_expr(p):
            return Tuple(p[0].values + (p[2], ))

        @self.pg.error
        def error_handle(token):
            throw(info, token, 'SyntaxError', 'invalid syntax')

    def get_parser(self, info: ModuleInfo, /) -> LRParser:
        self.add_syntaxes(info)
        return self.pg.build()


def get_parser(info: ModuleInfo, /, *, log: str = 'default') -> LRParser:
    if log == 'full':
        return Parser().get_parser(info)
    elif log == 'default':
        with catch_warnings(record=True) as warnings:
            parser = Parser().get_parser(info)

            warning_unused = True
            unused_tokens = []

            for warning in warnings:
                if warning.category is not ParserGeneratorWarning:
                    continue

                if warning_unused and (result := match(
                    r"^Token '(.+)' is unused$", f'{warning.message}'
                )):
                    unused_tokens.append(result.group(1))
                else:
                    if warning_unused:
                        warning_unused = False
                        if len(unused_tokens) == 1:
                            print(f"\x1b[91mParserGeneratorWarning: "
                                  f"Token '{unused_tokens}' is unused\x1b[0m")
                        elif len(unused_tokens) > 1:
                            token_string = ', '.join(
                                f"'{token}'" for token in unused_tokens
                            )
                            print(f"\x1b[91mParserGeneratorWarning: "
                                  f"Token {token_string} are unused\x1b[0m")
                    print(f'\x1b[91mParserGeneratorWarning: '
                          f'{warning.message}\x1b[0m')

        return parser
    elif log == 'none':
        with catch_warnings():
            filterwarnings('ignore')
            return Parser().get_parser(info)
    else:
        raise ValueError(f"param log must be 'full', 'default', or 'none', "
                         f"not {log!r}")


def informed(node: Ast, info: ModuleInfo) -> Ast:
    if node is None:
        raise ValueError('cannot inform a node of None')

    node.info = info
    for field in node._fields:
        value = getattr(node, field)
        if isinstance(value, Ast):
            setattr(node, field, informed(value, info))
        elif isinstance(value, list):
            setattr(node, field, [informed(item, info) for item in value])
        elif isinstance(value, tuple):
            setattr(node, field, tuple(informed(item, info) for item in value))
    return node


def parse(source: str, *, path: str = '<unknown>',
          log: str = 'default') -> Module:
    tokens = lex(source)

    info = ModuleInfo(source, path)

    parser = get_parser(info, log=log)

    try:
        module = parser.parse(tokens)
    except LexingError as err:
        index = err.source_pos.idx
        lineno = source[:index].count('\n')
        line = source.split('\n')[lineno]
        if '\n' in source[:index]:
            padding = (index - source[:index].rfind('\n')) * ' '
        else:
            padding = index * ' '
        exit(f'  File "{path}", line {lineno + 1}\n'
             f'    {line}\n'
             f'   {padding}^\n'
             f'SyntaxError: invalid syntax')

    return informed(module, info)
