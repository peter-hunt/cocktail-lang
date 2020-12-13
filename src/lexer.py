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


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # keywords
        self.lexer.add('BREAK', r'break')
        self.lexer.add('CONTINUE', r'continue')
        self.lexer.add('ELIF', r'elif')
        self.lexer.add('ELSE', r'else')
        self.lexer.add('FUNC', r'func')
        self.lexer.add('IF', r'if')
        self.lexer.add('IN', r'in')
        self.lexer.add('NOT', r'not')
        self.lexer.add('WHILE', r'while')
        # Identifiers
        self.lexer.add('NAME', r'[A-Za-z_]\w*')
        # Constants
        self.lexer.add(
            'NUMBER',
            (r'\d+(\.(\d+)?)?([Ee][+\-]?\d+)?'
             r'|(\d+)?\.\d+([Ee][+\-]?\d+)?'),
        )
        self.lexer.add(
            'STRING',
            (r'"[^"\n\\]*((\\.)*[^"\n\\]*)*(\\.)*"'
             r"|'[^'\n\\]*((\\.)*[^'\n\\]*)*(\\.)*'")
        )

        # Parenthesis
        self.lexer.add('LPAR', r'\(')
        self.lexer.add('RPAR', r'\)')
        # Brackets
        self.lexer.add('LSQB', r'\[')
        self.lexer.add('RSQB', r'\]')
        # Braces
        self.lexer.add('LBRACE', r'\{')
        self.lexer.add('RBRACE', r'\}')

        # Punctuations (Multi-Character)
        self.lexer.add('ELLIPSIS', r'\.\.\.')
        # Punctuations
        self.lexer.add('COMMA', r',')
        self.lexer.add('DOT', r'\.')
        self.lexer.add('COLON', r':')
        self.lexer.add('SEMI', r';')
        self.lexer.add('RARROW', r'\->')

        # Comparison Operations (Multi-Character)
        self.lexer.add('EQEQEQUAL', r'===')
        self.lexer.add('NOTEQEQEQUAL', r'!==')
        self.lexer.add('LESSEQUAL', r'<=')
        self.lexer.add('EQEQUAL', r'==')
        self.lexer.add('NOTEQUAL', r'!=')
        self.lexer.add('GREATEREQUAL', r'>=')
        # Mathematical/Bitwise Operations (Multi-Character)
        self.lexer.add('DOUBLESLASH', r'//')
        self.lexer.add('DOUBLESTAR', r'\*\*')
        self.lexer.add('LEFTSHIFT', r'<<')
        self.lexer.add('RIGHTSHIFT', r'>>')
        # In-place Operations (Multi-Character)
        self.lexer.add('PLUSEQUAL', r'\+=')
        self.lexer.add('MINUSEQUAL', r'\-=')
        self.lexer.add('STAREQUAL', r'\*=')
        self.lexer.add('ATEQUAL', r'@=')
        self.lexer.add('SLASHEQUAL', r'/=')
        self.lexer.add('DOUBLESLASHEQUAL', r'//=')
        self.lexer.add('PERCENTEQUAL', r'%=')
        self.lexer.add('DOUBLESTAREQUAL', r'\*\*=')
        self.lexer.add('LEFTSHIFTEQUAL', r'<<=')
        self.lexer.add('RIGHTSHIFTEQUAL', r'>>=')
        self.lexer.add('AMPEREQUAL', r'&=')
        self.lexer.add('CIRCUMFLEXEQUAL', r'\^=')
        self.lexer.add('VBAREQUAL', r'\|=')
        # Comparison Operations
        self.lexer.add('LESS', r'<')
        self.lexer.add('GREATER', r'>')
        # Mathematical/Bitwise Operations
        self.lexer.add('PLUS', r'\+')
        self.lexer.add('MINUS', r'\-')
        self.lexer.add('STAR', r'\*')
        self.lexer.add('AT', r'@')
        self.lexer.add('SLASH', r'/')
        self.lexer.add('PERCENT', r'%')
        self.lexer.add('AMPER', r'&')
        self.lexer.add('CIRCUMFLEX', r'\^')
        self.lexer.add('VBAR', r'\|')
        # Unary Operations
        self.lexer.add('TILDE', r'~')
        # Assignment Operations
        self.lexer.add('EQUAL', r'=')

        # Ignore Spaces
        self.lexer.ignore(r'\s+')
        self.lexer.ignore(r'\#.+\n')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
