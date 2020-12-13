"""
The Cocktail Lang.
  The Cocktail Lang helps you to create speedy and beautiful code easily.

Usage:
  cocktail [options] ... [-c cmd | <file>]

Options:
  --help -h   Show this help message and exit (also --help)
  -c cmd      Execute the line of code (also --version)
  --version -v  Show Cocktail version number and exit (also --version)
"""

from pathlib import Path

from docopt import docopt

from __init__ import __version__
from src.cocktail import run


def main():
    args = docopt(__doc__, version=f'Cocktail {__version__}')
    if args['<file>']:
        path = Path(args['<file>'])

        if not path.exists():
            self_path = Path(__file__)
            exit(f'{self_path}: {path}: No such file or directory')
        elif path.is_dir():
            self_path = Path(__file__)
            exit(f'{self_path}: {path}: Is a directory')

        with open(path) as file:
            source = file.read()

        run(source, path=f'{path}')

    elif args['-c'] is not None:
        run(args['-c'], path='<string>')

    else:
        exit(__doc__.split('\n\n')[1].strip())


if __name__ == '__main__':
    main()
