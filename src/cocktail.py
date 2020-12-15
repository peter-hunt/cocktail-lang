from re import match
from warnings import catch_warnings, filterwarnings

from rply.errors import LexingError, ParserGeneratorWarning

from .lexer import lex
from .moduleinfo import ModuleInfo
from .parser import get_parser


def parse(source, *, path='<unknown>'):
    tokens = lex(source)

    with catch_warnings(record=True) as warnings:
        parser = get_parser(info=ModuleInfo(source, path))

        warning_unused = True
        unused_tokens = []

        for warning in warnings:
            if warning.category is not ParserGeneratorWarning:
                continue

            if warning_unused and (result := match(r"^Token '(.+)' is unused$",
                                                   f'{warning.message}')):
                unused_tokens.append(result.group(1))
            else:
                if warning_unused:
                    warning_unused = False
                    if len(unused_tokens) == 1:
                        print(f"\x1b[91mParserGeneratorWarning: "
                              f"Token '{unused_tokens}' is unused\x1b[0m")
                    elif len(unused_tokens) > 1:
                        token_string = ', '.join(f"'{token}'"
                                                 for token in unused_tokens)
                        print(f"\x1b[91mParserGeneratorWarning: "
                              f"Token {token_string} are unused\x1b[0m")
                print(f'\x1b[91mParserGeneratorWarning: '
                      f'{warning.message}\x1b[0m')

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
