from typing import Self, Literal
from test_utils.build_tokens import BuildTokens
from data_types.token_type import TokenType
from data_types.lexical_token import Token
from enum import Enum

Initializers = Literal["none", "var_declaration", "expression"]
Conditions = Literal["none", "expression"]
Increment = Literal["none", "expression"]
Body = Literal["empty_block", "print_statement"]


class ForStmtTokenBuilder:
    def __init__(self) -> None:
        self.token_builder = BuildTokens()

        self.token_builder.keyword("for")
        self.token_builder.open_paren()

    def initializer(self, initializer_type: str) -> Self:
        if initializer_type == "var_declaration":
            self.token_builder.declare_var().identifier("i").assign().num(0)
        elif initializer_type == "expression":
            pass
        self.token_builder.semicolon()
        return self

    def condition(self, condition_type: str) -> Self:
        if condition_type == "less_than_10":
            self.token_builder.identifier("i").less_than().num(10)

        self.token_builder.semicolon()
        return self

    def increment(self, increment_type: str) -> Self:
        if increment_type == "increment_by_one":
            self.token_builder.identifier("i").assign().identifier("i").add().num(1)

        self.token_builder.close_paren()
        return self

    def body(self, body_type: str) -> Self:
        if body_type == "empty_block":
            self.token_builder.open_brace()
            self.token_builder.close_brace()
        elif body_type == "print_statement":
            self.token_builder.keyword("print")
            self.token_builder.identifier("i")
        return self

    def build(self) -> list[Token]:
        return self.token_builder.build()
