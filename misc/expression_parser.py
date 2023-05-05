from typing import Protocol
from data_types.lexical_token import Token
from data_types.token_type import TokenType
from data_types.errors import ParseError
from data_types.expr import *
from data_types.stmt import *

"""
This is the initial version of the parser that only parses expressions.
"""


class ErrorReporter(Protocol):
    def set_error(self, line: int, message: str) -> None:
        ...


class Parser:
    """
    Maps a sequence of tokens to expressions.

    The class has two types of methods:

    1. Methods help to manage the token stream and to ensure that tokens are properly consumed and processed.
       isEOF, peek, consume_token, consume_token_if_matching, check_token_type, next_token_matches, and synchronize.

    2. Methods that are used by the parse method to construct Expr objects based on the grammar of the input language.
        expression, term, factor, and primary
    """

    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter
        self.tokens: list[Token] = []
        self.pos: int = 0  # Points to the next token to be consumed
        self.expressions: list[Expr] = []

    def isEOF(self) -> bool:
        return self.tokens[self.pos].type == TokenType.EOF

    def peek(self) -> Token:
        """
        This method performs a one token 'lookahead' and does not consume the token.
        It looks at the current unconsumed token.

        Assumptions:
        Does not check isEOF. Assumes that 'self.pos' is not out of bounds.
        """
        return self.tokens[self.pos]

    def check_token_type(self, token_type: TokenType) -> bool:
        """
        Returns true if the current token is of the given type.
        Used as a helper method for 'next_token_matches'.
        """
        if self.isEOF():
            return False
        return self.peek().type == token_type

    def next_token_matches(self, token_types: list[TokenType]) -> bool:
        """
        Checks to see if the current token has any of the given types. If so,
        it returns True, otherwise it returns False.
        """
        for token_type in token_types:
            if self.check_token_type(token_type):
                return True

        return False

    def consume_token(self) -> Token:
        """
        Consumes the next token in the token stream and returns it.

        Assumptions:
        Does not check isEOF. Assumes that 'self.pos' is not out of bounds.
        """
        curr_token = self.tokens[self.pos]
        self.pos += 1
        return curr_token

    def consume_token_if_matching(self, token_type: TokenType, message: str) -> Token:
        """
        Consumes a token only if it matches the expected 'token_type', otherwise it throws a ParseError.

        Cetain expressions expect a certain order of tokens to be fully parsed (ex. STRING / NUMBER to create a Literal, semicolon to end an Expr etc.).
        """

        if self.next_token_matches([token_type]):
            return self.consume_token()
        raise ParseError(self.peek(), message)

    def synchronize(self) -> None:
        """
        Discard tokens until an expression boundary is found (i.e. a semicolon).

        This method is called after a ParseException occurs in order to return the parser
        to a valid state so that it can report several errors in one run, rather than exiting
        after every single error.
        """

        while not self.isEOF():
            self.consume_token()

            if self.next_token_matches([TokenType.SEMICOLON]):
                self.consume_token()
                return

    def _reset_parser(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.expressions = []

    def parse(self, tokens: list[Token]) -> list[Expr]:
        """
        Throws an "IndexError: list index out of range" exception if the tokens list is empty.
        Throws an "IndexError" if "EOF" token is missing.
        """
        self._reset_parser(tokens)

        while not self.isEOF():
            try:
                expr = self.expression()
                self.expressions.append(expr)
            except ParseError as e:
                self.synchronize()
                self.error_reporter.set_error(1, e.message)

        return self.expressions

    def expression(self) -> Expr:
        expr = self.term()
        self.consume_token_if_matching(TokenType.SEMICOLON, "Expected semicolon.")

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.next_token_matches([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator = self.consume_token()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.next_token_matches(
            [TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL]
        ):
            operator = self.consume_token()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.next_token_matches([TokenType.MINUS, TokenType.PLUS]):
            operator = self.consume_token()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.next_token_matches([TokenType.SLASH, TokenType.STAR]):
            operator = self.consume_token()
            right = self.primary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.next_token_matches([TokenType.BANG, TokenType.MINUS]):
            operator = self.consume_token()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def grouping(self) -> Expr:
        if self.next_token_matches([TokenType.LEFT_PAREN]):
            self.consume_token()  # Consume ')'
            expr = self.expression()
            self.consume_token_if_matching(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        return self.primary()

    def primary(self) -> Expr:
        # Convert Lox literals to Python literals
        if self.next_token_matches([TokenType.TRUE]):
            self.consume_token()
            return Literal(True)
        if self.next_token_matches([TokenType.FALSE]):
            self.consume_token()
            return Literal(False)
        if self.next_token_matches([TokenType.NIL]):
            self.consume_token()
            return Literal(None)

        if self.next_token_matches([TokenType.IDENTIFIER]):
            return Variable(self.consume_token())

        if self.next_token_matches([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self.consume_token().literal)

        raise ParseError(self.consume_token(), "Expect expression.")
