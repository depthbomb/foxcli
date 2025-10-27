from typing import Optional, TYPE_CHECKING
from foxcli.command_info import CommandInfo

if TYPE_CHECKING:
    from foxcli.command import Command

class CommandRegistry:
    def __init__(self):
        self._commands: dict[tuple[str, ...], type['Command']] = {}
        self._aliases: dict[str, tuple[str, ...]] = {}

    def register(self, command_class: type['Command'], parent: Optional[str] = None):
        name = command_class.name or command_class.__name__.lower()

        if parent:
            path = (parent, name)
        else:
            path = (name,)

        self._commands[path] = command_class

        # register aliases
        for alias in command_class.aliases:
            if parent:
                alias_path = (parent, alias)
            else:
                alias_path = (alias,)
            self._aliases[alias] = path
            self._commands[alias_path] = command_class

    def get(self, *path: str) -> Optional[type['Command']]:
        # try direct path
        cmd = self._commands.get(path)
        if cmd:
            return cmd

        # try resolving aliases
        if path and path[0] in self._aliases:
            resolved = self._aliases[path[0]]
            if len(path) > 1:
                resolved = resolved + path[1:]

            return self._commands.get(resolved)

        return None

    def get_command_info(self, *path: str) -> Optional[CommandInfo]:
        cmd = self.get(*path)
        return cmd.get_info() if cmd else None

    def list_commands(self, parent: Optional[str] = None) -> list[CommandInfo]:
        commands = []
        for path, cmd_class in self._commands.items():
            # skip aliases
            if path in self._aliases.values():
                continue

            # filter by parent
            if parent is None and len(path) == 1:
                commands.append(cmd_class.get_info())
            elif parent and len(path) == 2 and path[0] == parent:
                commands.append(cmd_class.get_info())

        return commands
