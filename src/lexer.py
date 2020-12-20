from re import match

from rply import LexerGenerator as RplyLexerGenerator
from rply.lexer import LexerStream, Lexer

from .ast import (
    Add, Sub, Mult, Div, FloorDiv, Mod, Pow, LShift, RShift,
    BitAnd, BitXor, BitOr,

    Lt, LtE, Eq, NotEq, Gt, GtE, Is, IsNot, In, NotIn,

    Invert, Not, UAdd, USub,
)
from .obj import BooleanType, NoneType


__all__ = [
    'TOKEN_PATTERNS',
    'IGNORED_PATTERNS',
    'TOKENS',
    'BIN_OP',
    'INPLACE_OP',
    'CMP_OP',
    'UNARY_OP',
    'LexerGenerator',
    'lexer',
    'lex',
]


TOKEN_PATTERNS = {
    # keywords
    'BREAK': r'break',
    'CONTINUE': r'continue',
    'ELIF': r'elif',
    'ELSE': r'else',
    'FUNC': r'func',
    'IF': r'if',
    'IN': r'in',
    'NOT': r'not',
    'WHILE': r'while',
    # Identifiers
    'NAME': r'[A-Za-z_]\w*',
    # Constants
    'NUMBER': (r'\d+(\.(\d+)?)?([Ee][+\-]?\d+)?'
               r'|(\d+)?\.\d+([Ee][+\-]?\d+)?'),
    'STRING': (r'"[^"\n\\]*((\\.)*[^"\n\\]*)*(\\.)*"'
               r"|'[^'\n\\]*((\\.)*[^'\n\\]*)*(\\.)*'"),

    # Parenthesis
    'LPAR': r'\(', 'RPAR': r'\)',
    # Brackets
    'LSQB': r'\[', 'RSQB': r'\]',
    # Braces
    'LBRACE': r'\{', 'RBRACE': r'\}',

    # Punctuations (Multi-Character)
    'ELLIPSIS': r'\.\.\.',
    # Punctuations
    'COMMA': r',',
    'DOT': r'\.',
    'COLON': r':',
    'SEMI': r';',
    'RARROW': r'\->',

    # In-place Operations (Multi-Character)
    'DOUBLESLASHEQUAL': r'//=',
    'PLUSEQUAL': r'\+=',
    'MINUSEQUAL': r'\-=',
    'STAREQUAL': r'\*=',
    'ATEQUAL': r'@=',
    'SLASHEQUAL': r'/=',
    'PERCENTEQUAL': r'%=',
    'DOUBLESTAREQUAL': r'\*\*=',
    'LEFTSHIFTEQUAL': r'<<=',
    'RIGHTSHIFTEQUAL': r'>>=',
    'AMPEREQUAL': r'&=',
    'CIRCUMFLEXEQUAL': r'\^=',
    'VBAREQUAL': r'\|=',
    # Comparison Operations (Multi-Character)
    'EQEQEQUAL': r'===',
    'NOTEQEQEQUAL': r'!==',
    'LESSEQUAL': r'<=',
    'EQEQUAL': r'==',
    'NOTEQUAL': r'!=',
    'GREATEREQUAL': r'>=',
    # Mathematical/Bitwise Operations (Multi-Character)
    'DOUBLESLASH': r'//',
    'DOUBLESTAR': r'\*\*',
    'LEFTSHIFT': r'<<',
    'RIGHTSHIFT': r'>>',
    # Comparison Operations
    'LESS': r'<',
    'GREATER': r'>',
    # Mathematical/Bitwise Operations
    'PLUS': r'\+',
    'MINUS': r'\-',
    'STAR': r'\*',
    'AT': r'@',
    'SLASH': r'/',
    'PERCENT': r'%',
    'AMPER': r'&',
    'CIRCUMFLEX': r'\^',
    'VBAR': r'\|',
    # Unary Operations
    'TILDE': r'~',
    # Assignment Operations
    'EQUAL': r'=',
}

IGNORED_PATTERNS = [
    r'\s+',
    r'\#.+\n',
    r'/\*[\s\S]*\*/',
]

TOKENS = [*TOKEN_PATTERNS]

BIN_OP = {
    'PLUS': Add,
    'MINUS': Sub,
    'STAR': Mult,
    'SLASH': Div,
    'DOUBLESLASH': FloorDiv,
    'PERCENT': Mod,
    'DOUBLESTAR': Pow,
    'LEFTSHIFT': LShift,
    'RIGHTSHIFT': RShift,
    'AMPER': BitAnd,
    'CIRCUMFLEX': BitXor,
    'VBAR': BitOr,
}

INPLACE_OP = {
    'PLUSEQUAL': Add,
    'MINUSEQUAL': Sub,
    'STAREQUAL': Mult,
    'SLASHEQUAL': Div,
    'DOUBLESLASHEQUAL': FloorDiv,
    'PERCENTEQUAL': Mod,
    'DOUBLESTAREQUAL': Pow,
    'LEFTSHIFTEQUAL': LShift,
    'RIGHTSHIFTEQUAL': RShift,
    'AMPEREQUAL': BitAnd,
    'CIRCUMFLEXEQUAL': BitXor,
    'VBAREQUAL': BitOr,
}

CMP_OP = {
    'LESS': Lt,
    'LESSEQUAL': LtE,
    'EQEQUAL': Eq,
    'NOTEQUAL': NotEq,
    'GREATER': Gt,
    'GREATEREQUAL': GtE,
    'EQEQEQUAL': Is,
    'NOTEQEQEQUAL': IsNot,
    'IN': In,
    ('NOT', 'IN'): NotIn,
}

UNARY_OP = {
    'TILDE': Invert,
    'NOT': Not,
    'PLUS': UAdd,
    'MINUS': USub,
}


class LexerGenerator:
    def __init__(self, /) -> None:
        self.lexer = RplyLexerGenerator()

    def add_tokens(self, /) -> None:
        for name, pattern in TOKEN_PATTERNS.items():
            if match(r'^[a-z]+$', pattern):
                self.lexer.add(name, f'\\b{pattern}\\b')
            else:
                self.lexer.add(name, pattern)

        for pattern in IGNORED_PATTERNS:
            self.lexer.ignore(pattern)

    def get_lexer(self, /) -> Lexer:
        self.add_tokens()
        return self.lexer.build()


lexer_generator = LexerGenerator()
lexer = lexer_generator.get_lexer()


def lex(source: str) -> LexerStream:
    return lexer.lex(source)
