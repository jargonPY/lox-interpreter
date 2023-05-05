import pytest
from parser.parser import Parser
from data_types.lexical_token import Token
from data_types.errors import ParseError
from test_utils.build_tokens import BuildTokens
from test_utils.error_reporter import TestErrorReporter
from lox import Lox


def setup_lox() -> Lox:
    return Lox()


def test_parse_literal():
    text = "1234"
    lox = setup_lox()

    expressions = lox.run(text)

    assert repr(expressions) == "[1234]"
