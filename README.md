_foxcli_ is a minimal-by-design CLI framework for Python built around argparse.

There are many great CLI frameworks out there, but some features I like in one aren't present in another. Likewise, one framework I like may have features that I don't like or has a bunch of extra features that I don't need.

This framework features:

- Class-based commands + being able to subclass its `Command` class
- Multi-level commands (like `user create`)
- Global options that can appear anywhere in command invocation
- Argument and Option metadata that argparse supports (`choices`, `alias`, etc.)

foxcli is still very much in early development but certainly usable, in fact I am using it in a testdrive with my project [WinUtils](https://github.com/depthbomb/winutils)!

# Sample

```py
from sys import exit
from foxcli.cli import CLI
from typing import Annotated
from foxcli.option import Option
from foxcli.command import Command
from foxcli.argument import Argument

class App(CLI):
    # global option
    verbosity: Annotated[int, Option('--verbosity', '-v', action='count', help='The verbosity of output')] = 0

class DeleteEverythingCommand(Command):
    def run(self, app: App):
        if app.verbosity >= 3:  # access global options
            self.stdout.write('\nGlobbing C:\\Windows\\System32...')  # can also access stdin and stderr
        
        self.stdout.write('\nDeleting everything!')
        return 0

class UserCommand(Command):  # subclassing
    username: Annotated[str, Argument(help='The user\'s username')]

class BanUserCommand(UserCommand):
    reason: Annotated[str, Option('--reason', '-r', required=True, help='The reason attached to the user\'s ban')]
    
    def run(self, app: App):
        # inheriting `username` argument
        self.stdout.write('\nBanning %s for %s...' % (self.username, self.reason))
        return 0

class UnbanUserCommand(UserCommand):
    def run(self, app: App):
        self.stdout.write('\nUnbanning %s...' % self.username)
        return 0

app = App(name='myapp', version='1.0.0', description='My Cool CLI App')
app.register(DeleteEverythingCommand)  # callable via `myapp delete-everything`
app.register(BanUserCommand, path=['user', 'ban'])  # callable via `myapp user ban`
app.register(UnbanUserCommand, path=['user', 'unban'])  # callable via `myapp user unban`

exit(app.run())
```
