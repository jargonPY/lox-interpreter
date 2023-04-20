from typing import Protocol, Self
from data_types.lexical_token import Token


class EnvironmentProtocol(Protocol):
    def __init__(self, parent_env: Self | None = None) -> None:
        ...

    def assign(self, variable_name: Token, value: object) -> None:
        ...

    def define(self, variable_name: str, value: object) -> None:
        ...

    def get(self, variable_name: Token):
        ...

    def get_at(self, distance: int, variable_name: str) -> object:
        ...

    def assign_at(self, distance: int, variable_name: str, value: object) -> None:
        ...
