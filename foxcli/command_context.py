import sys
from typing import Optional, TYPE_CHECKING
from foxcli.command_info import CommandInfo
from foxcli.arg_accessor import ArgAccessor
from foxcli.command_registry import CommandRegistry

if TYPE_CHECKING:
    from foxcli.cli import CLI

class CommandContext:
    def __init__(
        self,
        global_options: ArgAccessor,
        registry: CommandRegistry,
        cli: 'CLI',
        stdin=None,
        stdout=None,
        stderr=None
    ):
        self.global_options = global_options
        self.registry = registry
        self.cli = cli
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def get_command_info(self, *path: str) -> Optional[CommandInfo]:
        return self.registry.get_command_info(*path)

    def list_commands(self, parent: Optional[str] = None) -> list[CommandInfo]:
        return self.registry.list_commands(parent)
