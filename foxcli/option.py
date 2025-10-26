from typing import Any, Union, Optional
from dataclasses import field, dataclass

@dataclass
class Option:
    names: list[str] = field(default_factory=list)
    help: str = ''
    action: Optional[str] = None
    choices: Optional[list[Any]] = None
    nargs: Optional[Union[str, int]] = None

    def __init__(
            self,
            *names: str,
            help: str = '',
            required: bool = False,
            action: Optional[str] = None,
            choices: Optional[list[Any]] = None,
            nargs: Optional[Union[str, int]] = None,
    ):
        self.names = list(names)
        self.help = help
        self.required = required
        self.action = action
        self.choices = choices
        self.nargs = nargs
