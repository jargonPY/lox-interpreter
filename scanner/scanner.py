from typing import Protocol
from data_types.lexical_token import Token
from data_types.token_type import TokenType
from data_types.keywords import KEYWORDS
from data_types.error_messages import *

"""
Formatting - https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html

The main method consumes the current character and pattern matches it to a helper method.
The helper method then scans/consumes the rest of the lexeme and returns a token.

The question is how to best share the current_char between the main method and the helper method?
    - Current solution is for helper methods to access the current character throught the current_char
      property method.
    - Once the functionality is set-up and tests are passing, it can be easily refactored.

DON'T SPEND TIME OPTIMIZING ON FIRST PASS. Just get it to work and then refactor.
"""


class ErrorReporter(Protocol):
    def set_error(self, line: int, message: str) -> None:
        ...


EOF_LEXEME = "/0"


class Scanner:
    """
    Maps a sequence of characters to tokens.
    """

    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter
        self.text: str = ""
        self.pos: int = 0  # Points to the next character to be consumed
        self.line: int = 1
        self.tokens: list[Token] = []

    @property
    def current_char(self) -> str:
        # ? What if its accessed before a token is consumed, it will return the last char?
        return self.text[self.pos - 1]

    def peek(self) -> str:
        """
        This method performs a one character 'lookahead' and does not consume the character.
        It looks at the current unconsumed character.
        """
        if self.isEOF():
            return EOF_LEXEME
        return self.text[self.pos]

    def peekNext(self) -> str:
        """
        This method performs a two character lookahead, skipping the token to be consumed next.
        """
        if self.pos + 1 >= len(self.text):
            return EOF_LEXEME
        return self.text[self.pos + 1]

    def isEOF(self) -> bool:
        return self.pos >= len(self.text)

    def consume_char(self) -> str:
        """
        Consumes the next character in the source file and returns it.
        """
        curr_char = self.text[self.pos]
        self.pos += 1
        return curr_char

    def _reset_scanner(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.tokens = []

    def scan(self, text: str) -> list[Token]:
        self._reset_scanner(text)

        while not self.isEOF():
            curr_char = self.consume_char()

            if curr_char in [" ", "\r", "\t", "\n"]:
                # todo group all non-token-producing cases into a seperate function
                continue  # Need to add 'continue' to every case that doesn't produce a 'token'

            if curr_char.isdigit():
                token = self.scan_number()
            elif curr_char == '"':
                token = self.scan_string()

            # Single character lexemes
            elif curr_char == "+":
                token = Token(TokenType.PLUS, curr_char)
            elif curr_char == "-":
                token = Token(TokenType.MINUS, curr_char)
            elif curr_char == "*":
                token = Token(TokenType.STAR, curr_char)
            elif curr_char == "/":
                token = Token(TokenType.SLASH, curr_char)
            elif curr_char == ";":
                token = Token(TokenType.SEMICOLON, curr_char)
            elif curr_char == ".":
                token = Token(TokenType.DOT, curr_char)
            elif curr_char == ",":
                token = Token(TokenType.COMMA, curr_char)
            elif curr_char == "(":
                token = Token(TokenType.LEFT_PAREN, curr_char)
            elif curr_char == ")":
                token = Token(TokenType.RIGHT_PAREN, curr_char)
            elif curr_char == "{":
                token = Token(TokenType.LEFT_BRACE, curr_char)
            elif curr_char == "}":
                token = Token(TokenType.RIGHT_BRACE, curr_char)

            elif curr_char == "/n":
                self.line += 1
                continue

            # Single or double character lexemes
            elif curr_char == "!":
                if self.peek() == "=":
                    curr_char += self.consume_char()
                    token = Token(TokenType.BANG_EQUAL, curr_char)
                else:
                    token = Token(TokenType.BANG, curr_char)
            elif curr_char == "=":
                if self.peek() == "=":
                    curr_char += self.consume_char()
                    token = Token(TokenType.EQUAL_EQUAL, curr_char)
                else:
                    token = Token(TokenType.EQUAL, curr_char)
            elif curr_char == "<":
                if self.peek() == "=":
                    curr_char += self.consume_char()
                    token = Token(TokenType.LESS_EQUAL, curr_char)
                else:
                    token = Token(TokenType.LESS, curr_char)
            elif curr_char == ">":
                if self.peek() == "=":
                    curr_char += self.consume_char()
                    token = Token(TokenType.GREATER_EQUAL, curr_char)
                else:
                    token = Token(TokenType.GREATER, curr_char)

            # Matching reserved words and identifiers
            elif curr_char.isalpha():
                token = self.scan_identifier()
            else:
                """
                What happens if a user throws a source file containing some characters Lox doesn’t use, like @#^, at our interpreter?
                Right now, those characters get silently discarded. They aren’t used by the Lox language, but that doesn’t mean the
                interpreter can pretend they aren’t there. Instead, we report an error.

                Note that the erroneous character is still consumed by the earlier call to advance(). That’s important so that we don’t
                get stuck in an infinite loop.

                Note also that we keep scanning. There may be other errors later in the program. It gives our users a better experience
                if we detect as many of those as possible in one go. Otherwise, they see one tiny error and fix it, only to have the next
                error appear, and so on. Syntax error Whac-A-Mole is no fun.

                (Don’t worry. Since hadError gets set, we’ll never try to execute any of the code, even though we keep going and scan the rest of it.)

                The code reports each invalid character separately, so this shotguns the user with a blast of errors if they accidentally paste a big
                blob of weird text. Coalescing a run of invalid characters into a single error would give a nicer user experience.
                """
                self.error_reporter.set_error(self.line, INVALID_CHAR)
                continue
                # raise ValueError("Invalid character")

            self.tokens.append(token)

        self.tokens.append(Token(TokenType.EOF, EOF_LEXEME, None))
        return self.tokens

    def scan_number(self) -> Token:
        curr_number = self.current_char  # ? Does this shallow copy the sub-string?

        while self.peek().isdigit() or self.peek() == ".":
            curr_number += self.consume_char()

        return Token(TokenType.NUMBER, curr_number, float(curr_number))

    def scan_string(self) -> Token:
        string = ""

        while self.peek() != '"' and not self.isEOF():
            if self.peek() == "\n":
                self.line += 1

            string += self.consume_char()

        if self.isEOF():
            self.error_reporter.set_error(self.line, UNTERMINATED_STRING)
        else:
            self.consume_char()  # Consume the last '"'

        return Token(TokenType.STRING, string, string)

    def scan_identifier(self) -> Token:
        identifier = self.current_char

        while self.peek().isalpha() or self.peek().isdigit():
            identifier += self.consume_char()

        # Checks if the identifier’s lexeme is one of the reserved words.
        # If so, we use that keyword’s token type. Otherwise, it’s a regular user-defined identifier.
        if identifier in KEYWORDS.keys():
            return Token(KEYWORDS[identifier], identifier)

        return Token(TokenType.IDENTIFIER, identifier)
