#!/usr/bin/env python3
"""
Tester for Cocktail Lang

Usage:
    test <program-id> [options]
"""

from pathlib import Path

try:
    from cocktail.docopt import docopt
except (ImportError, ModuleNotFoundError):
    from docopt import docopt

from cocktail.run import execute


def main(argv=None):
    args = docopt(__doc__, argv)

    if args['<program-id>'] is not None:
        program_id = args['<program-id>']
        path = Path(f'tests/{program_id}.cocktail')

        if not path.exists():
            exit(f'{Path(__file__)}: {path}: No such file or directory')
        elif path.is_dir():
            exit(f'{Path(__file__)}: {path}: Is a directory')

        with open(path) as file:
            execute(file.read())


if __name__ == '__main__':
    main()
