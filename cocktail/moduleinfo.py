from dataclasses import dataclass


__all__ = ['ModuleInfo']


@dataclass
class ModuleInfo:
    source: str
    path: str = '<unknown>'
