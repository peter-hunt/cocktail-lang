from rply import Token

from .moduleinfo import ModuleInfo


__all__ = ['throw']


def throw(info: ModuleInfo, token: Token, error: str = 'Error', msg: str = '',
          *, line: bool = False) -> None:
    if not isinstance(info, ModuleInfo):
        print(info, token)
        print(f'{error}: {msg}')
        exit()
    pos = token.getsourcepos()
    source_line = info.source.split('\n')[pos.lineno - 1]

    if line:
        pointer = ''
    else:
        padding = ' ' * (pos.colno - 1)
        pointer = f'    {padding}^\n'

    exit(f'  File "{info.path}", line {pos.lineno}\n'
         f'    {source_line}\n'
         f'{pointer}'
         f'{error}: {msg}')
