import sys
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Type, TextIO, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from foxcli.core.cli import CLI

@dataclass
class CommandInfo:
    name: str
    path: list[str]
    description: str
    aliases: list[str]
    doc: Optional[str]
    cls: Type['Command']

class Command(ABC):
    def __init__(self):
        self.stdin: TextIO = sys.stdin
        self.stdout: TextIO = sys.stdout
        self.stderr: TextIO = sys.stderr
        self._commands: dict[str, CommandInfo] = {}

    def _set_io(self, stdin: TextIO, stdout: TextIO, stderr: TextIO):
        """Set I/O streams"""
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def _set_commands(self, commands: dict[str, CommandInfo]):
        """Injects command registry"""
        self._commands = commands

    def get_command(self, name: str) -> Optional[CommandInfo]:
        """Gets information about a registered command by name or path"""
        return self._commands.get(name)

    def list_commands(self) -> list[CommandInfo]:
        """Lists all registered commands"""
        return list(self._commands.values())

    @abstractmethod
    def run(self, app: 'CLI') -> int:
        pass
