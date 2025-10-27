from typing import Optional
from foxcli.option import Option
from foxcli.argument import Argument
from foxcli.command_info import CommandInfo
from foxcli.arg_accessor import ArgAccessor
from foxcli.command_context import CommandContext

class Command:
    name: str = ''
    description: str = ''
    aliases: list[str] = []
    arguments: list[Argument] = []
    options: list[Option] = []
    ctx: Optional[CommandContext] = None

    @classmethod
    def get_all_arguments(cls) -> list[Argument]:
        arguments = []
        for base in reversed(cls.__mro__):
            if base is Command or not issubclass(base, Command):
                continue

            if hasattr(base, 'arguments') and base.arguments:
                existing_names = {arg.name for arg in arguments}
                for arg in base.arguments:
                    if arg.name not in existing_names:
                        arguments.append(arg)

        return arguments

    @classmethod
    def get_all_options(cls) -> list[Option]:
        options = []
        for base in reversed(cls.__mro__):
            if base is Command or not issubclass(base, Command):
                continue

            if hasattr(base, 'options') and base.options:
                existing_names = {opt.name for opt in options}
                for opt in base.options:
                    if opt.name not in existing_names:
                        options.append(opt)

        return options

    def run(self, args: ArgAccessor) -> int:
        raise NotImplementedError
    
    @classmethod
    def get_info(cls) -> CommandInfo:
        return CommandInfo(
            name=cls.name or cls.__name__.lower(),
            description=cls.description,
            aliases=cls.aliases,
            doc=cls.__doc__
        )
