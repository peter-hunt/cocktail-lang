from warnings import filterwarnings

from rply.errors import LexingError, ParserGeneratorWarning

from .lexer import Lexer
from .moduleinfo import ModuleInfo
from .parser import Parser


def parse(source, *, path='<unknown>'):
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)

    # Ignore unused-token errors for early development
    filterwarnings('ignore', r'Token .+ is unused', ParserGeneratorWarning)
    pg = Parser()
    pg.parse(ModuleInfo(source, path))

    parser = pg.get_parser()
    try:
        module = parser.parse(tokens)
    except LexingError as err:
        idx = err.source_pos.idx
        lineno = source[:idx].count('\n')
        line = source.split('\n')[lineno]
        if '\n' in source[:idx]:
            padding = (idx - source[:idx].rfind('\n')) * ' '
        else:
            padding = idx * ' '
        colno = source[:idx].rfind('\n')
        exit(f'  File "example/test.cocktail", line {lineno + 1}\n'
             f'    {line}\n'
             f'   {padding}^\n'
             f'SyntaxError: invalid syntax')
    else:
        return module


def run(source, *, path='<unknown>'):
    parse(source, path=path).eval()
