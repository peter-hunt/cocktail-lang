from typing import Iterator

from rply import Token
from rply.errors import LexingError

from .lexer import lex
from .parser import parse


__all__ = ['tokenize', 'execute']


def tokenize(source: str, /, *, path: str = '<unknown>') -> Iterator[Token]:
    try:
        for token in lex(source):
            yield token
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


def execute(source: str, /,
            *, path: str = '<unknown>', log: str = 'default') -> None:
    parse(source, path=path, log=log).eval()
