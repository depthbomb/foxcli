from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

@dataclass
class Option(Generic[T]):
    name: str
    short: Optional[str] = None
    default: Optional[T] = None
    required: bool = False
    help: str = ''

    @property
    def flag_names(self) -> list[str]:
        name = self.name.replace('--', '')
        names = [f'--{name}']

        if self.short:
            short = self.short.replace('-', '')
            names.append(f'-{short}')

        return names

Opt = Option
