def throw(info, token, error='Error', msg='', *, line=False):
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
