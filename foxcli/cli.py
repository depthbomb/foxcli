import sys
from typing import Any, Optional
from foxcli.option import Option
from foxcli.command import Command
from foxcli.argument import Argument
from foxcli.arg_accessor import ArgAccessor
from foxcli.parsed_command import ParsedCommand
from foxcli.command_context import CommandContext
from foxcli.command_registry import CommandRegistry

class CLI:
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        global_options: Optional[list[Option]] = None
    ):
        self.name = name
        self.version = version
        self.description = description
        self.global_options = global_options or []
        self.registry = CommandRegistry()

    def command(self, parent: Optional[str] = None):
        def decorator(cls: type[Command]) -> type[Command]:
            self.registry.register(cls, parent)
            return cls

        return decorator

    register = command  # TODO would 'register' make more sense than 'command`?

    def _parse_args(self, argv: list[str]) -> ParsedCommand:
        args = argv[1:]  # skip program name

        global_opts, remaining = self._parse_options(args, self.global_options)

        command_path = []
        command_class = None

        for i, arg in enumerate(remaining):
            if arg.startswith('-'):
                break

            # try to find command
            test_path = command_path + [arg]
            cmd = self.registry.get(*test_path)
            if cmd:
                command_path = test_path
                command_class = cmd
            else:
                # not a command, treat as arguments
                break

        if not command_class:
            raise ValueError(f'Unknown command: {' '.join(remaining)}')

        # remove command path from remaining args
        remaining = remaining[len(command_path):]

        # parse command-specific options and arguments (including inherited ones)
        cmd_opts, positional = self._parse_options(
            remaining,
            command_class.get_all_options()
        )

        # parse positional arguments according to Argument definitions (including inherited ones)
        parsed_args = self._parse_arguments(positional, command_class.get_all_arguments())

        return ParsedCommand(
            command_path=command_path,
            command_class=command_class,
            parsed_args=parsed_args,
            options=cmd_opts,
            global_options=global_opts
        )

    def _parse_arguments(self, positional: list[str], arguments: list[Argument]) -> dict[str, Any]:
        parsed = {}
        pos_idx = 0

        for arg_def in arguments:
            if pos_idx >= len(positional):
                # no more positional args available
                if arg_def.required and arg_def.default is None:
                    raise ValueError(f'Missing required argument: {arg_def.name}')

                parsed[arg_def.name] = arg_def.default
                continue
            if arg_def.nargs == 1:
                # single argument
                parsed[arg_def.name] = self._coerce_argument(
                    positional[pos_idx],
                    arg_def
                )
                pos_idx += 1
            elif arg_def.nargs == '?':
                # zero or one
                if pos_idx < len(positional):
                    parsed[arg_def.name] = self._coerce_argument(
                        positional[pos_idx],
                        arg_def
                    )
                    pos_idx += 1
                else:
                    parsed[arg_def.name] = arg_def.default
            elif arg_def.nargs == '*':
                # zero or more - consume remaining
                values = []
                while pos_idx < len(positional):
                    values.append(self._coerce_argument(
                        positional[pos_idx],
                        arg_def
                    ))
                    pos_idx += 1

                parsed[arg_def.name] = values
            elif arg_def.nargs == '+':
                # one or more
                if pos_idx >= len(positional):
                    raise ValueError(f'Argument {arg_def.name} requires at least one value')

                values = []
                while pos_idx < len(positional):
                    values.append(self._coerce_argument(
                        positional[pos_idx],
                        arg_def
                    ))
                    pos_idx += 1

                parsed[arg_def.name] = values
            elif isinstance(arg_def.nargs, int):
                # exact count
                if pos_idx + arg_def.nargs > len(positional):
                    raise ValueError(
                        f'Argument {arg_def.name} requires {arg_def.nargs} values, '
                        f'got {len(positional) - pos_idx}'
                    )

                values = []
                for _ in range(arg_def.nargs):
                    values.append(self._coerce_argument(
                        positional[pos_idx],
                        arg_def
                    ))
                    pos_idx += 1

                parsed[arg_def.name] = values if arg_def.nargs > 1 else values[0]

        if pos_idx < len(positional):
            unused = positional[pos_idx:]
            raise ValueError(f'Unexpected arguments: {', '.join(unused)}')

        return parsed

    def _coerce_argument(self, value: str, argument: Argument) -> Any:
        if argument.default is None:
            return value

        target_type = type(argument.default)

        if target_type == bool:
            return value.lower() in ('true', '1', 'yes', 'y')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == list:
            return value

        return value

    def _parse_options(self, args: list[str], options: list[Option]) -> tuple[dict[str, Any], list[str]]:
        parsed = {}
        positional = []
        i = 0

        opt_map: dict[str, Option] = {}
        for opt in options:
            for flag in opt.flag_names:
                opt_map[flag] = opt

        while i < len(args):
            arg = args[i]
            if arg == '--':
                positional.extend(args[i + 1:])
                break

            if arg.startswith('-'):
                if '=' in arg:
                    flag, value = arg.split('=', 1)
                    if flag in opt_map:
                        opt = opt_map[flag]
                        parsed[opt.name] = self._coerce_value(value, opt)
                        i += 1
                        continue
                    else:
                        positional.append(arg)
                        i += 1
                        continue
                if arg in opt_map:
                    opt = opt_map[arg]

                    expects_value = not (opt.default is False or opt.default is True)
                    if expects_value and i + 1 < len(args) and not args[i + 1].startswith('-'):
                        value = args[i + 1]
                        parsed[opt.name] = self._coerce_value(value, opt)
                        i += 2
                    else:
                        if isinstance(opt.default, bool):
                            parsed[opt.name] = True
                            i += 1
                        elif expects_value and opt.required:
                            raise ValueError(f'Option {arg} requires a value')
                        else:
                            parsed[opt.name] = opt.default
                            i += 1
                else:
                    positional.append(arg)
                    i += 1
            else:
                positional.append(arg)
                i += 1

        for opt in options:
            if opt.name not in parsed:
                if opt.required:
                    raise ValueError(f'Required option --{opt.name} not provided')

                parsed[opt.name] = opt.default

        return parsed, positional

    def _coerce_value(self, value: str, option: Option) -> Any:
        if option.default is None:
            return value

        target_type = type(option.default)

        if target_type == bool:
            return value.lower() in ('true', '1', 'yes', 'y')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)

        return value

    def run(self, argv: Optional[list[str]] = None) -> int:
        if argv is None:
            argv = sys.argv

        try:
            parsed = self._parse_args(argv)

            ctx = CommandContext(
                global_options=ArgAccessor(parsed.global_options),
                registry=self.registry,
                cli=self
            )

            command = parsed.command_class(ctx)
            accessor = ArgAccessor({**parsed.parsed_args, **parsed.options})

            return command.run(accessor)
        except Exception as e:
            # TODO make this overrideable
            print(f'Error: {e}', file=sys.stderr)
            return 1
