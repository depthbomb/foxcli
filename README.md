from cli import UnknownCommandError> [!IMPORTANT]
> While foxcli is pre-1.0.0, breaking changes may be made without bumping the major version!

_foxcli_ is a minimal-by-design CLI framework for Python.

There are many great CLI frameworks out there, but some features I like in one aren't present in another. Likewise, one framework I like may have features that I don't like or has a bunch of extra features that I don't need.

foxcli being minimal-by-design means that it does not include any built-in commands, no TUI helpers, no command usage generation. You will have to handle all of this yourself.

This framework features:

- Class-based commands + being able to subclass its `Command` class
- Multi-level commands (like `user create`)
- Global options that can appear anywhere in command invocation
- Hooks to customize error handling

foxcli is still very much in early development but certainly usable, in fact I am using it in a testdrive with my project [WinUtils](https://github.com/depthbomb/winutils)!

Planned features include:

- Counted arguments like `-vvv`

# Installation

```shell
pip install foxcli
```

# Sample

```py
from sys import exit
from foxcli.cli import CLI
from foxcli.command import Command
from foxcli.argument import Argument
from foxcli.option import Opt, Option

class App(CLI):
    # hooks to customize error handling
    def on_unknown_command(self, e):
        # command not found, show a custom usage message?
        return 1

app = App(
    name='myapp',
    version='1.0.0',
    description='My app',
    global_options=[
        # global options, accessible in commands via `self.ctx.global_options`
        Option(name='verbose', short='v', default=False, help='Show verbose output'),
    ]
)

@app.command()
class Version(Command):
    name = 'version'
    description = 'Show version'

    def run(self, args) -> int:
        print(self.ctx.cli.version)
        return 0

# subclassing `Command` to add options
class UserableCommand(Command):
    arguments = [
        Argument('username'),  # supports `nargs` which takes int, '*', '+', and '?'. defaults to 1, which implicitly makes it required
    ]

@app.command()
class User(Command):
    name = 'user'
    aliases = ['u']
    description = 'User management commands'

# multi-level command
@app.command(parent='user')
class UserCreate(UserableCommand):
    name = 'create'
    description = 'Creates a new user'
    aliases = ['c', 'add']
    arguments = [
        # positional arguments
        Argument('avatar', default='https://website.com/image.png'),  # supports default values
    ]
    options = [
        Opt('rank', short='r', required=True)  # shortcut for `Option`, `Arg` also exists
    ]

    # `myapp user add Caim -r "Super Admin" -v`
    def run(self, args) -> int:
        # self.ctx.global_options.get('verbose', bool) -> True
        print(self.ctx.global_options.to_dict())  # {'verbose': True}

        # args.get('username', str) -> 'Caim'
        # args.get('avatar', str) -> 'https://website.com/image.png'
        # args.get('rank', str) -> 'Super Admin'
        print(args.to_dict())  # {'username': 'Caim', 'avatar': 'https://website.com/image.png', 'rank': 'Super Admin'}
        return 0

exit(app.run())
```
