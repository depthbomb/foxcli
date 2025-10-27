from dataclasses import dataclass
from typing import Union, TypeVar, Generic, Literal, Optional

T = TypeVar('T')

@dataclass
class Argument(Generic[T]):
    name: str
    default: Optional[T] = None
    required: bool = True
    nargs: Union[int | Literal['*', '+', '?']] = 1  # int for exact count, '*' for zero or more, '+' for one or more, '?' for zero or one
    help: str = ''


Arg = Argument
