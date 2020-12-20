"""
The Cocktail Lang.
  The Cocktail Lang helps you to create speedy and beautiful code easily.

Usage:
  cocktail [options] ... [-c cmd | <file>] [-o output]

Options:
  --ast -a      Parse the file and output the abstract syntax tree
  -c cmd        Execute the line of code
  --help -h     Show this help message and exit
  --lex -l      Lex the file and output the tokens
  -o output     Print the output to the file
  --version -v  Show Cocktail version number and exit
"""

from pathlib import Path
from sys import stdout

from docopt import docopt

from __init__ import __version__
from src.astprint import astprint
from src.lexer import lex
from src.run import execute, tokenize
from src.moduleinfo import ModuleInfo
from src.parser import get_parser


def _get_file(args):
    if args['-o'] is not None:
        output = Path(args['-o'])

        if output.is_dir():
            exit(f'{Path(__file__)}: {output}: Is a directory')

        return open(output, 'w+')
    else:
        return stdout


def main():
    args = docopt(__doc__, version=f'Cocktail {__version__}')
    if args['<file>']:
        output_used = args['-o'] is not None
        output = _get_file(args)

        path = Path(args['<file>'])

        if not path.exists():
            exit(f'{Path(__file__)}: {path}: No such file or directory')
        elif path.is_dir():
            exit(f'{Path(__file__)}: {path}: Is a directory')

        with open(path) as file:
            source = file.read()

        if args['--lex']:
            for token in tokenize(source, path=path):
                print(token, file=output)
        elif args['--ast']:
            tokens = lex(source)

            parser = get_parser(
                ModuleInfo(source, f'{path}'),
                log='none' if output_used else 'default',
            )
            ast = parser.parse(tokens)

            print(ast, file=output)
            astprint(ast, file=output)
        else:
            execute(source, path=f'{path}')

    elif args['-c'] is not None:
        execute(args['-c'], path='<string>')

    else:
        exit(__doc__.split('\n\n')[1].strip())


if __name__ == '__main__':
    main()
