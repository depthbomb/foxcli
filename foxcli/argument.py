from dataclasses import dataclass
from typing import Any, Union, Optional

@dataclass
class Argument:
    help: str = ''
    default: Optional[Any] = None
    choices: Optional[list[Any]] = None
    nargs: Optional[Union[str, int]] = None

Arg = Argument
