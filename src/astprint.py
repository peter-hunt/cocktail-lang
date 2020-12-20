from contextlib import contextmanager
from sys import stdout
from typing import Any, Generator, Union

from rply.token import Token

from .ast import Ast, ExprContent


__all__ = ['astformat', 'astprint']


def _is_sub_node(node: Any) -> bool:
    return isinstance(node, Ast) and not isinstance(node, ExprContent)


def _is_leaf(node: Ast) -> bool:
    for field in node._fields:
        if not hasattr(node, field):
            raise ValueError(f'field {field!r} not found for node {node}')
        attr = getattr(node, field)
        if _is_sub_node(attr):
            return False
        elif isinstance(attr, (list, tuple)):
            for val in attr:
                if _is_sub_node(val):
                    return False
    else:
        return True


def _leaf(node: Any) -> str:
    if isinstance(node, Ast):
        content = ', '.join(
            f'{field}={_leaf(getattr(node, field))}'
            for field in node._fields
        )
        return f'{type(node).__name__}({content})'
    elif isinstance(node, list):
        return '[{}]'.format(', '.join(_leaf(x) for x in node))
    elif isinstance(node, tuple):
        return '({})'.format(', '.join(_leaf(x) for x in node))
    elif isinstance(node, type):
        return f'{node.__name__}()'
    else:
        return f'{node!r}'


def astformat(
    node: Any,
    indent: str = '  ',
    _indent: int = 0,
) -> str:
    if node is None or isinstance(node, (float, int, str)):
        return f'{node!r}'
    elif isinstance(node, (list, tuple)) or _is_leaf(node):
        return _leaf(node)
    else:
        class state:
            indent = _indent

        @contextmanager
        def indented() -> Generator[None, None, None]:
            state.indent += 1
            yield
            state.indent -= 1

        def indentstr() -> str:
            return state.indent * indent

        def _astformat(el: Union[Ast, None, str], _indent: int = 0) -> str:
            return astformat(el, indent=indent, _indent=_indent)

        out = f'{type(node).__name__}(\n'
        with indented():
            for field in node._fields:
                attr = getattr(node, field)
                if attr == []:
                    representation = '[]'
                elif (isinstance(attr, list) and len(attr) == 1 and
                      isinstance(attr[0], Ast) and _is_leaf(attr[0])):
                    representation = f'[{_astformat(attr[0])}]'
                elif isinstance(attr, list):
                    representation = '[\n'
                    with indented():
                        for el in attr:
                            representation += '{}{},\n'.format(
                                indentstr(), _astformat(el, state.indent)
                            )
                    representation += f'{indentstr()}]'
                elif (isinstance(attr, tuple) and len(attr) == 1 and
                      isinstance(attr[0], Ast) and _is_leaf(attr[0])):
                    representation = f'({_astformat(attr[0])},)'
                elif isinstance(attr, tuple):
                    representation = '(\n'
                    with indented():
                        for el in attr:
                            representation += '{}{},\n'.format(
                                indentstr(), _astformat(el, state.indent)
                            )
                    representation += f'{indentstr()})'
                elif isinstance(attr, Ast):
                    representation = _astformat(attr, state.indent)
                elif isinstance(attr, type):
                    representation = attr.__name__
                else:
                    representation = f'{attr!r}'
                out += f'{indentstr()}{field}={representation},\n'
        out += f'{indentstr()})'
        return out


def astprint(node: Any, indent: str = '  ', _indent: int = 0,
             sep=' ', end='\n', file=stdout, flush=False) -> None:
    print(astformat(node, indent, _indent),
          sep=sep, end=end, file=file, flush=flush)
