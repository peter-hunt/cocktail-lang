from rply import LexerGenerator

from .ast import (
    Add, Sub, Mult, Div, FloorDiv, Mod, Pow, LShift, RShift,
    BitAnd, BitXor, BitOr,

    Lt, LtE, Eq, NotEq, Gt, GtE, Is, IsNot, In, NotIn,

    Invert, Not, UAdd, USub,
)
from .obj import BooleanType, NoneType


TOKENS = [
    # Keywords
    'BREAK',
    'CONTINUE',
    'ELIF',
    'ELSE',
    'FUNC',
    'IF',
    'IN',
    'NOT',
    'WHILE',
    # Identifiers
    'NAME',
    # Constants
    'NUMBER',
    'STRING',

    # Parenthesis
    'LPAR',
    'RPAR',
    # Brackets
    'LSQB',
    'RSQB',
    # Braces
    'LBRACE',
    'RBRACE',

    # Punctuations
    'COMMA',
    'DOT',
    'COLON',
    'SEMI',
    'RARROW',
    'ELLIPSIS',

    # Comparison Operations
    'LESS',
    'LESSEQUAL',
    'EQEQUAL',
    'NOTEQUAL',
    'GREATER',
    'GREATEREQUAL',
    'EQEQEQUAL',
    'NOTEQEQEQUAL',
    # Mathematical/Bitwise Operations
    'PLUS',
    'MINUS',
    'STAR',
    'AT',
    'SLASH',
    'DOUBLESLASH',
    'PERCENT',
    'DOUBLESTAR',
    'LEFTSHIFT',
    'RIGHTSHIFT',
    'AMPER',
    'CIRCUMFLEX',
    'VBAR',
    # Unary Operations
    'TILDE',
    # In-place Operations
    'EQUAL',
    'PLUSEQUAL',
    'MINUSEQUAL',
    'STAREQUAL',
    'ATEQUAL',
    'SLASHEQUAL',
    'DOUBLESLASHEQUAL',
    'PERCENTEQUAL',
    'DOUBLESTAREQUAL',
    'LEFTSHIFTEQUAL',
    'RIGHTSHIFTEQUAL',
    'AMPEREQUAL',
    'CIRCUMFLEXEQUAL',
    'VBAREQUAL',
]

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


class Lexer:
    def __init__(self):
        self.lexer = LexerGenerator()

    def add(self, name, pattern, flags=0):
        assert name in TOKENS
        self.lexer.add(name, pattern, flags)

    def add_tokens(self):
        # keywords
        self.add('BREAK', r'break')
        self.add('CONTINUE', r'continue')
        self.add('ELIF', r'elif')
        self.add('ELSE', r'else')
        self.add('FUNC', r'func')
        self.add('IF', r'if')
        self.add('IN', r'in')
        self.add('NOT', r'not')
        self.add('WHILE', r'while')
        # Identifiers
        self.add('NAME', r'[A-Za-z_]\w*')
        # Constants
        self.add(
            'NUMBER',
            (r'\d+(\.(\d+)?)?([Ee][+\-]?\d+)?'
             r'|(\d+)?\.\d+([Ee][+\-]?\d+)?'),
        )
        self.add(
            'STRING',
            (r'"[^"\n\\]*((\\.)*[^"\n\\]*)*(\\.)*"'
             r"|'[^'\n\\]*((\\.)*[^'\n\\]*)*(\\.)*'")
        )

        # Parenthesis
        self.add('LPAR', r'\(')
        self.add('RPAR', r'\)')
        # Brackets
        self.add('LSQB', r'\[')
        self.add('RSQB', r'\]')
        # Braces
        self.add('LBRACE', r'\{')
        self.add('RBRACE', r'\}')

        # Punctuations (Multi-Character)
        self.add('ELLIPSIS', r'\.\.\.')
        # Punctuations
        self.add('COMMA', r',')
        self.add('DOT', r'\.')
        self.add('COLON', r':')
        self.add('SEMI', r';')
        self.add('RARROW', r'\->')

        # In-place Operations (Multi-Character)
        self.add('DOUBLESLASHEQUAL', r'//=')
        self.add('PLUSEQUAL', r'\+=')
        self.add('MINUSEQUAL', r'\-=')
        self.add('STAREQUAL', r'\*=')
        self.add('ATEQUAL', r'@=')
        self.add('SLASHEQUAL', r'/=')
        self.add('PERCENTEQUAL', r'%=')
        self.add('DOUBLESTAREQUAL', r'\*\*=')
        self.add('LEFTSHIFTEQUAL', r'<<=')
        self.add('RIGHTSHIFTEQUAL', r'>>=')
        self.add('AMPEREQUAL', r'&=')
        self.add('CIRCUMFLEXEQUAL', r'\^=')
        self.add('VBAREQUAL', r'\|=')
        # Comparison Operations (Multi-Character)
        self.add('EQEQEQUAL', r'===')
        self.add('NOTEQEQEQUAL', r'!==')
        self.add('LESSEQUAL', r'<=')
        self.add('EQEQUAL', r'==')
        self.add('NOTEQUAL', r'!=')
        self.add('GREATEREQUAL', r'>=')
        # Mathematical/Bitwise Operations (Multi-Character)
        self.add('DOUBLESLASH', r'//')
        self.add('DOUBLESTAR', r'\*\*')
        self.add('LEFTSHIFT', r'<<')
        self.add('RIGHTSHIFT', r'>>')
        # Comparison Operations
        self.add('LESS', r'<')
        self.add('GREATER', r'>')
        # Mathematical/Bitwise Operations
        self.add('PLUS', r'\+')
        self.add('MINUS', r'\-')
        self.add('STAR', r'\*')
        self.add('AT', r'@')
        self.add('SLASH', r'/')
        self.add('PERCENT', r'%')
        self.add('AMPER', r'&')
        self.add('CIRCUMFLEX', r'\^')
        self.add('VBAR', r'\|')
        # Unary Operations
        self.add('TILDE', r'~')
        # Assignment Operations
        self.add('EQUAL', r'=')

        # Ignore Spaces
        self.lexer.ignore(r'\s+')
        self.lexer.ignore(r'\#.+\n')
        self.lexer.ignore(r'/\*[\s\S]*\*/')

    def get_lexer(self):
        self.add_tokens()
        return self.lexer.build()
