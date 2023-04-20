import pytest
from parser.parser import Parser
from data_types.lexical_token import Token
from data_types.errors import ParseError
from data_types.error_messages import *
from test_utils.build_tokens import BuildTokens
from test_utils.error_reporter import TestErrorReporter
from test_utils.builders.for_statement_builder import ForStmtTokenBuilder

# ! If "parse()" does not throw an error, how to test that an error was thrown and properly handled?
# ! Focus on user-observed behaviour. The user would see an error message, so test that the same error message is visible.
# ! Another user is the interpreter so test that the correct set of expressions is returned (i.e. that synchronization works).

# todo extend reporter type include "message" attribute
# todo add the hard-coded messages to "error.py" and import them into parser and into test, that way its easy to change the message.


def setup_parser() -> Parser:
    return Parser(TestErrorReporter())


""" ========================= Parse Statement Tests ========================= """


def test_parse_variable_declaration_with_num():
    tokens = BuildTokens().declare_var().identifier("x").assign().num(10).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    assert repr(statement) == "[var x = 10]"


def test_parse_variable_declaration_with_expression():
    tokens = BuildTokens().declare_var().identifier("x").assign().num(10).add().num(100).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    assert repr(statement) == "[var x = (10 + 100)]"


def test_parse_variable_assignment():
    tokens = BuildTokens().identifier("x").assign().num(10).add().num(100).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    assert repr(statement) == "[x = (10 + 100)]"


def test_parse_invalid_assignment():
    tokens = BuildTokens().num(10).add().num(100).assign().num(10).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    assert statement == []
    assert parser.error_reporter.message == INVALID_ASSIGNMENT


def test_parse_block():
    pass


def test_parse_while_loop():
    pass


def test_parse_if_statement():
    pass


def test_parse_or_expression():
    pass


def test_parse_and_expression():
    pass


""" ========================= For Statement Tests ========================= """


def test_parse_for_loop_with_empty_block():
    tokens = ForStmtTokenBuilder().initializer("none").condition("none").increment("none").body("empty_block").build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    assert repr(statement) == "[while (true) {[]}]"


def test_parse_for_loop_with_single_statement():
    parser = setup_parser()
    tokens = (
        ForStmtTokenBuilder().initializer("none").condition("none").increment("none").body("print_statement").build()
    )

    statement = parser.parse(tokens)

    assert repr(statement) == "[while (true) print i;]"


def test_parse_for_loop_with_initializer():
    parser = setup_parser()
    tokens = (
        ForStmtTokenBuilder()
        .initializer("var_declaration")
        .condition("none")
        .increment("none")
        .body("empty_block")
        .build()
    )

    statement = parser.parse(tokens)

    assert repr(statement) == "[{['var i = 0', 'while (true) {[]}']}]"


""" ========================= Function Call Expression Tests ========================= """


def test_parse_function_call_with_zero_args():
    parser = setup_parser()
    tokens = BuildTokens().identifier("functionName").open_paren().close_paren().build()

    statement = parser.parse(tokens)
    print("ST: ", statement[0])

    assert repr(statement) == "[functionName([])]"


""" ========================= Parse Expression Tests ========================= """

# ! Need assertions that ensure that the parsed heirarchy is correct


def test_parse_literal():
    tokens = BuildTokens().num(1234).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert repr(expressions) == "[1234]"


def test_parse_binary():
    tokens = BuildTokens().num(1234).add().num(2124).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert repr(expressions) == "[(1234 + 2124)]"


def test_parse_div_precedence_right():
    tokens = BuildTokens().num(1234).add().num(2124).div().num(4).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert repr(expressions) == "[(1234 + (2124 / 4))]"


def test_parse_div_precedence_left():
    tokens = BuildTokens().num(1234).div().num(2124).add().num(4).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert repr(expressions) == "[((1234 / 2124) + 4)]"


def test_multiple_expressions():
    tokens = BuildTokens().num(1234).add().num(4).end_expr().num(10).div().num(2124).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert repr(expressions) == "[(1234 + 4), (10 / 2124)]"


""" ========================= Invalid Expression Exception Tests ========================= """


def test_invalid_binary():
    tokens = BuildTokens().num(1234).add().build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert expressions == []
    assert parser.error_reporter.message == "Expect expression."


""" ========================= Missing Semicolon Exception Tests ========================= """


def test_two_expressions_missing_semicolon():
    # * There is a ParseException between token "4" and token "10". It then syncs to the ending semicolon,
    # * never adding the expression to the expressions list, thus resulting is an empty list.
    tokens = BuildTokens().num(1234).add().num(4).num(10).div().num(2124).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert expressions == []
    assert parser.error_reporter.message == MISSING_SEMICOLON


def test_three_expressions_missing_semicolon():
    tokens = BuildTokens().num(1234).add().num(4).num(10).div().num(2124).end_expr().num(1234).add().num(4).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert repr(expressions) == "[(1234 + 4)]"
    assert parser.error_reporter.message == MISSING_SEMICOLON


""" ========================= IndexError Exception Tests ========================= """


def test_parse_empty_token_list():
    tokens = []
    parser = setup_parser()

    with pytest.raises(IndexError):
        parser.parse(tokens)


def test_parse_eof():
    tokens = BuildTokens().build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    assert expressions == []


def test_parse_missing_eof():
    tokens = BuildTokens().num(10).build(include_eof=False)
    parser = setup_parser()

    with pytest.raises(IndexError):
        parser.parse(tokens)


def test_parse_missing_semicolon_and_eof():
    tokens = BuildTokens().num(10).div().num(10).build(include_semicolon=False, include_eof=False)
    parser = setup_parser()

    with pytest.raises(IndexError):
        parser.parse(tokens)
