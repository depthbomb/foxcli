from typing import Any, Type, Union, TypeVar, Literal, get_args, get_origin

T = TypeVar('T')

class ArgAccessor:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __str__(self):
        return str(self._data)

    def to_dict(self) -> dict[str, Any]:
        return self._data

    def get(self, key: str, as_type: Type[T]) -> T:
        if key not in self._data:
            raise KeyError(f'Key \'{key}\' not found')

        value = self._data[key]
        origin = get_origin(as_type)
        if origin is Literal:
            allowed_values = get_args(as_type)
            if value in allowed_values:
                return value

            raise TypeError(f'Value for \'{key}\' is not one of Literal{allowed_values}, got {value!r}')

        if origin is Union:
            allowed_types = get_args(as_type)
            if any((t is type(None) and value is None) or isinstance(value, t) for t in allowed_types):
                return value

            raise TypeError(f'Value for \'{key}\' is not one of {allowed_types}, got {type(value).__name__}')

        if not isinstance(value, as_type):
            raise TypeError(f'Value for \'{key}\' is not of type {as_type.__name__}, got {type(value).__name__}')

        return value
