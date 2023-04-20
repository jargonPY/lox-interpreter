from typing import Self
from data_types.token_type import TokenType
from data_types.lexical_token import Token
from data_types.keywords import KEYWORDS

# todo each 'TokenType' has an associated method, find a way to ensure that if more types are added there will be a type error
# todo showing that a corresponding method is missing, this will be useful for extending the syntax in the future


# ? Doesn't build "Expr" but rather a list of Tokens that represent an expression
class BuildTokens:
    def __init__(self) -> None:
        self.tokens: list[Token] = []

    def declare_var(self) -> Self:
        self.tokens.append(Token(TokenType.VAR, "var"))
        return self

    def identifier(self, name: str) -> Self:
        self.tokens.append(Token(TokenType.IDENTIFIER, name))
        return self

    def keyword(self, keyword: str) -> Self:
        self.tokens.append(Token(KEYWORDS[keyword], keyword))
        return self

    def string(self, string: str) -> Self:
        self.tokens.append(Token(TokenType.STRING, string, string))
        return self

    def num(self, number: int) -> Self:
        self.tokens.append(Token(TokenType.NUMBER, str(number), number))
        return self

    def add(self) -> Self:
        self.tokens.append(Token(TokenType.PLUS, "+", None))
        return self

    def sub(self) -> Self:
        self.tokens.append(Token(TokenType.MINUS, "-", None))
        return self

    def mult(self) -> Self:
        self.tokens.append(Token(TokenType.STAR, "*", None))
        return self

    def div(self) -> Self:
        self.tokens.append(Token(TokenType.SLASH, "/", None))
        return self

    def negate(self) -> Self:
        self.tokens.append(Token(TokenType.BANG, "!", None))
        return self

    def not_equal(self) -> Self:
        self.tokens.append(Token(TokenType.BANG_EQUAL, "!=", None))
        return self

    def assign(self) -> Self:
        self.tokens.append(Token(TokenType.EQUAL, "=", None))
        return self

    def equal(self) -> Self:
        self.tokens.append(Token(TokenType.EQUAL_EQUAL, "==", None))
        return self

    def less_than(self) -> Self:
        self.tokens.append(Token(TokenType.LESS, "<", None))
        return self

    def less_equal_than(self) -> Self:
        self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", None))
        return self

    def greater_than(self) -> Self:
        self.tokens.append(Token(TokenType.GREATER, ">", None))
        return self

    def greater_equal_than(self) -> Self:
        self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", None))
        return self

    def open_paren(self) -> Self:
        self.tokens.append(Token(TokenType.LEFT_PAREN, "(", None))
        return self

    def close_paren(self) -> Self:
        self.tokens.append(Token(TokenType.RIGHT_PAREN, ")", None))
        return self

    def open_brace(self) -> Self:
        self.tokens.append(Token(TokenType.LEFT_BRACE, "{", None))
        return self

    def close_brace(self) -> Self:
        self.tokens.append(Token(TokenType.RIGHT_BRACE, "}", None))
        return self

    # todo This method is identical to 'end_expr', change all references to 'end_expr' to use this method
    def semicolon(self) -> Self:
        self.tokens.append(Token(TokenType.SEMICOLON, ";", None))
        return self

    def end_expr(self) -> Self:
        """
        This method is used to end an expression, when several expressions are chained together.
        """
        self.tokens.append(Token(TokenType.SEMICOLON, ";", None))
        return self

    def build(self, include_semicolon=True, include_eof=True) -> list[Token]:
        if include_semicolon:
            self.tokens.append(Token(TokenType.SEMICOLON, ";", None))

        if include_eof:
            self.tokens.append(Token(TokenType.EOF, "/0", None))

        return self.tokens
