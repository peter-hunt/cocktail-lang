"""
The Cocktail Lang.
  The Cocktail Lang helps you to create speedy and beautiful code easily.

Usage:
  cocktail <file> [options]

Options:
  -h --help     Show this screen.
  -v --version  Show version.
  --var         Output module variables at the end of execution
"""

from pathlib import Path

from docopt import docopt

from __init__ import __version__
from src.cocktail import run


def main():
    args = docopt(__doc__, version=__version__)
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

        var = args['--var']

        result = run(source, path=f'{path}')
        if var:
            print(result)

    else:
        exit(__doc__.strip())


if __name__ == '__main__':
    main()
