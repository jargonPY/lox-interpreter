from typing import Union
from data_types.token_type import TokenType


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: Union[str, float, None] = None) -> None:
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal

    def __hash__(self) -> int:
        return hash((self.type, self.lexeme, self.literal))

    def __eq__(self, other: object):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.lexeme == other.lexeme and self.literal == other.literal

    def __repr__(self) -> str:
        return self.lexeme
