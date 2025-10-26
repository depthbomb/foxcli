import sys
from foxcli.option import Option
from foxcli.argument import Argument
from foxcli.command import Command, CommandInfo
from argparse import ArgumentParser, _SubParsersAction, RawDescriptionHelpFormatter
from typing import Any, Type, TextIO, Optional, get_args, Annotated, get_origin, get_type_hints

class CLI:
    def __init__(
        self,
        name: str,
        version: str = '',
        description: str = '',
        stdin: Optional[TextIO] = None,
        stdout: Optional[TextIO] = None,
        stderr: Optional[TextIO] = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

        self._parser = ArgumentParser(
            prog=name,
            description=description,
            formatter_class=RawDescriptionHelpFormatter,
        )
        self._subparsers = self._parser.add_subparsers(dest='command', help='Available commands')
        self._commands: dict[str, tuple[Type[Command], list[str], list[str]]] = {}
        self._command_info: dict[str, CommandInfo] = {}
        self._global_fields: dict[str, tuple[Any, Any]] = {}

        hints = get_type_hints(self.__class__, include_extras=True)

        for attr_name, hint in hints.items():
            if get_origin(hint) is Annotated:
                args = get_args(hint)
                if len(args) >= 2 and isinstance(args[1], Option):
                    opt = args[1]
                    default = getattr(self, attr_name, None)
                    self._global_fields[attr_name] = (opt, default)

                    kwargs = {'help': opt.help}
                    if default is not None:
                        kwargs['default'] = default
                    if opt.action:
                        kwargs['action'] = opt.action
                    elif args[0] == bool:
                        kwargs['action'] = 'store_true' if not default else 'store_false'
                    if opt.choices:
                        kwargs['choices'] = opt.choices

                    self._parser.add_argument(*opt.names, **kwargs)

    def register(
        self,
        command_cls: Type[Command],
        path: Optional[list[str]] = None,
        aliases: Optional[list[str]] = None,
    ) -> None:
        if path is None:
            path = [self._class_to_command_name(command_cls.__name__)]

        aliases = aliases or []
        command_name = '-'.join(path)

        self._commands[command_name] = (command_cls, path, aliases)
        self._command_info[command_name] = CommandInfo(
            name=command_name,
            path=path,
            description=command_cls.__doc__.strip() if command_cls.__doc__ else '',
            aliases=aliases,
            doc=command_cls.__doc__,
            cls=command_cls,
        )

        parser = self._subparsers
        subparser_cache = {}
        for i, segment in enumerate(path):
            is_last = i == len(path) - 1

            if is_last:
                cmd_parser = parser.add_parser(
                    segment,
                    help=command_cls.__doc__.strip() if command_cls.__doc__ else '',
                    aliases=aliases,
                    formatter_class=RawDescriptionHelpFormatter,
                )
                cmd_parser.set_defaults(_command_cls=command_cls, _command_name=command_name)

                for attr_name, (opt, default) in self._global_fields.items():
                    kwargs = {'help': opt.help}
                    if default is not None:
                        kwargs['default'] = default
                    if opt.action:
                        kwargs['action'] = opt.action
                        if opt.action == 'count' and 'default' not in kwargs:
                            kwargs['default'] = 0
                    else:
                        hints = get_type_hints(self.__class__, include_extras=True)
                        hint = hints[attr_name]
                        if get_args(hint)[0] == bool:
                            kwargs['action'] = 'store_true' if not default else 'store_false'
                    if opt.choices:
                        kwargs['choices'] = opt.choices
                    cmd_parser.add_argument(*opt.names, **kwargs)

                self._add_command_args(cmd_parser, command_cls)
            else:
                cache_key = '-'.join(path[:i+1])
                if cache_key in subparser_cache:
                    parser = subparser_cache[cache_key]
                else:
                    if hasattr(parser, '_name_parser_map') and segment in parser._name_parser_map:
                        existing = parser._name_parser_map[segment]
                        for action in existing._subparsers._group_actions:
                            if isinstance(action, _SubParsersAction):
                                parser = action
                                subparser_cache[cache_key] = parser
                                break
                    else:
                        sub = parser.add_parser(segment, help=f'{segment} commands')
                        parser = sub.add_subparsers(dest=f'subcommand_{i}')
                        subparser_cache[cache_key] = parser

    def _add_command_args(self, parser: ArgumentParser, command_cls: Type[Command]):
        all_hints = {}
        for base_cls in reversed(command_cls.__mro__):
            if base_cls is Command or base_cls is object:
                continue
            hints = get_type_hints(base_cls, include_extras=True)
            all_hints.update(hints)

        for attr_name, hint in all_hints.items():
            if get_origin(hint) is Annotated:
                args = get_args(hint)
                metadata = args[1] if len(args) >= 2 else None

                if isinstance(metadata, Argument):
                    kwargs = {'help': metadata.help}
                    if metadata.default is not None:
                        kwargs['default'] = metadata.default
                        if metadata.nargs is None:
                            kwargs['nargs'] = '?'
                    if metadata.nargs is not None:
                        kwargs['nargs'] = metadata.nargs
                    if metadata.choices:
                        kwargs['choices'] = metadata.choices

                    parser.add_argument(attr_name, **kwargs)
                elif isinstance(metadata, Option):
                    default_value = None
                    has_default = False
                    for base_cls in command_cls.__mro__:
                        if base_cls is Command or base_cls is object:
                            continue
                        if hasattr(base_cls, attr_name):
                            default_value = getattr(base_cls, attr_name)
                            has_default = True
                            break

                    kwargs = {'help': metadata.help}
                    if has_default:
                        kwargs['default'] = default_value
                    if metadata.action:
                        kwargs['action'] = metadata.action
                        if metadata.action == 'count' and 'default' not in kwargs:
                            kwargs['default'] = 0
                    elif args[0] == bool:
                        kwargs['action'] = 'store_true' if not default_value else 'store_false'

                    if metadata.nargs is not None:
                        if metadata.action not in ('store_true', 'store_false', 'store_const', 'count', 'append_const'):
                            kwargs['nargs'] = metadata.nargs

                    if metadata.choices:
                        kwargs['choices'] = metadata.choices

                    kwargs['required'] = metadata.required

                    parser.add_argument(*metadata.names, dest=attr_name, **kwargs)

    def run(self, argv: Optional[list[str]] = None) -> int:
        args = self._parser.parse_args(argv)

        for attr_name in self._global_fields:
            setattr(self, attr_name, getattr(args, attr_name))

        command_cls = getattr(args, '_command_cls', None)
        if not command_cls:
            self._parser.print_help(self.stderr)
            return 1

        command = command_cls()
        command._set_io(self.stdin, self.stdout, self.stderr)
        command._set_commands(self._command_info)

        for base_cls in command_cls.__mro__:
            if base_cls is Command or base_cls is object:
                continue
            hints = get_type_hints(base_cls, include_extras=True)
            for attr_name in hints:
                if hasattr(args, attr_name):
                    setattr(command, attr_name, getattr(args, attr_name))

        return command.run(self)

    @staticmethod
    def _class_to_command_name(class_name: str) -> str:
        class_name = class_name.replace('Command', '')
        result = []
        for i, c in enumerate(class_name):
            if c.isupper() and i > 0:
                result.append('-')
            result.append(c.lower())
        return ''.join(result)
