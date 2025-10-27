from typing import Any
from dataclasses import dataclass
from foxcli.command import Command

@dataclass
class ParsedCommand:
    command_path: list[str]
    command_class: type[Command]
    parsed_args: dict[str, Any]
    options: dict[str, Any]
    global_options: dict[str, Any]
