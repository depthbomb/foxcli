# 10/27/2025

## 0.4.1

- Classes that subclass `Command` can now have a constructor

## 0.4.0

- Also make parsed args and options accessible in `Command` classes from `self.ctx.args`
- Added hooks:
  - `on_invalid_argument_count` - Called when an argument has the incorrect value number of values
  - `on_missing_option_value` - Called when an option is expecting a value but does not receive one
  - `on_missing_required_argument` - Called when a positional argument is missing
  - `on_missing_required_option` - Called when a required option is missing
  - `on_no_command` - Called when no arguments are passed to the program
  - `on_unexpected_arguments` - Called when more arguments than expected are passed to the program
  - `on_unknown_command` - Called when an unknown command is called
  - `on_error` - Called when any other exception is raised, such as during command execution

## 0.3.0

- Major rewrite

---

# 10/25/2025

## 0.2.0

- Make `version` arg on CLI required
- Add `Opt` and `Arg` aliases for `Option` and `Argument`

## 0.1.0

- Initial
