import pytest
from parser.parser import Parser
from data_types.lexical_token import Token
from data_types.errors import ParseError
from data_types.error_messages import *
from data_types.stmt import ExpressionStmt
from test_utils.build_tokens import BuildTokens
from test_utils.error_reporter import TestErrorReporter
from test_utils.builders.for_statement_builder import ForStmtTokenBuilder
from test_utils.builders.expression_builders import *
from test_utils.builders.statement_builders import *

# ! If "parse()" does not throw an error, how to test that an error was thrown and properly handled?
# ! Focus on user-observed behaviour. The user would see an error message, so test that the same error message is visible.
# ! Another user is the interpreter so test that the correct set of expressions is returned (i.e. that synchronization works).

# todo extend reporter type include "message" attribute.
# todo add the hard-coded messages to "error.py" and import them into parser and into test, that way its easy to change the message.
# todo come up with a better way to wrap "Expr" in "ExpressionStmt" and "Expr" / "Stmt" in "[]".


def setup_parser() -> Parser:
    return Parser(TestErrorReporter())


""" ========================= Parse Variable Declaration Tests ========================= """


def test_parse_variable_declaration_with_num():
    tokens = BuildTokens().declare_var().identifier("x").assign().num(10).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    expected_stmt = build_variable_declaration(variable_name="x", initializer=build_literal(10))
    assert statement == [expected_stmt]


def test_parse_variable_declaration_with_expression():
    tokens = BuildTokens().declare_var().identifier("x").assign().num(10).add().num(100).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    var_initializer = build_binary(build_literal(10), "add", build_literal(100))
    expected_stmt = build_variable_declaration(variable_name="x", initializer=var_initializer)
    assert statement == [expected_stmt]


""" ========================= Parse Variable Assignment Tests ========================= """


def test_parse_variable_assignment():
    tokens = BuildTokens().identifier("x").assign().num(10).add().num(100).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    value = build_binary(build_literal(10), "add", build_literal(100))
    expected_stmt = build_assign("x", value)
    assert statement == [ExpressionStmt(expected_stmt)]


def test_parse_invalid_assignment():
    tokens = BuildTokens().num(10).add().num(100).assign().num(10).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    assert statement == []
    assert parser.error_reporter.message == INVALID_ASSIGNMENT


""" ========================= Parse Block Statement Tests ========================= """


def test_parse_block():
    pass


""" ========================= Parse If Statement Tests ========================= """


def test_parse_if_statement():
    tokens = BuildTokens().keyword("if").open_paren().keyword("true").close_paren().keyword("print").num("if").build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    condition = build_literal(True)
    then_branch = build_print(build_literal("if"))
    expected_stmt = build_if(condition, then_branch, None)
    assert statement == [expected_stmt]


""" ========================= Parse Logical Expressions ("and" / "or") Tests ========================= """


def test_parse_or_expression():
    tokens = BuildTokens().num(10).keyword("or").num(100).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    expected_expr = build_logical(build_literal(10), "or", build_literal(100))
    assert expressions == [ExpressionStmt(expected_expr)]


def test_parse_and_expression():
    tokens = BuildTokens().num(10).keyword("and").num(100).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    expected_expr = build_logical(build_literal(10), "and", build_literal(100))
    assert expressions == [ExpressionStmt(expected_expr)]


""" ========================= Parse While Statement Tests ========================= """


def test_parse_while_loop():
    tokens = BuildTokens().keyword("while").open_paren().keyword("true").close_paren().keyword("print").num(10).build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    condition = build_literal(True)
    body = build_print(build_literal(10))
    expected_stmt = build_while(condition, body)
    assert statement == [expected_stmt]


""" ========================= For Statement Tests ========================= """


def test_parse_for_loop_with_empty_block():
    tokens = ForStmtTokenBuilder().initializer("none").condition("none").increment("none").body("empty_block").build()
    parser = setup_parser()

    statement = parser.parse(tokens)

    expected_stmt = build_while(build_literal(True), build_block([]))
    assert statement == [expected_stmt]
    # assert repr(statement) == "[while (true) {[]}]"


def test_parse_for_loop_with_single_statement():
    parser = setup_parser()
    tokens = (
        ForStmtTokenBuilder().initializer("none").condition("none").increment("none").body("print_statement").build()
    )

    statement = parser.parse(tokens)

    body = build_print(build_variable(variable_name="i"))
    expected_stmt = build_while(build_literal(True), body)
    assert statement == [expected_stmt]
    # assert repr(statement) == "[while (true) print i;]"


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

    var_decl = build_variable_declaration(variable_name="i", initializer=build_literal(0))
    while_loop = build_while(build_literal(True), build_block([]))
    expected_stmt = build_block([var_decl, while_loop])
    assert statement == [expected_stmt]
    # assert repr(statement) == "[{['var i = 0', 'while (true) {[]}']}]"


""" ========================= Function Call Expression Tests ========================= """


def test_parse_function_call_with_zero_args():
    parser = setup_parser()
    tokens = BuildTokens().identifier("functionName").open_paren().close_paren().build()

    statement = parser.parse(tokens)

    callee = build_variable(variable_name="functionName")
    expected_expr = build_function_call(callee, [])
    assert statement == [ExpressionStmt(expected_expr)]


""" ========================= Parse Expression Tests ========================= """

# ! Need assertions that ensure that the parsed heirarchy is correct


def test_parse_literal():
    tokens = BuildTokens().num(1234).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    expected_expr = build_literal(1234)
    assert expressions == [ExpressionStmt(expected_expr)]


def test_parse_binary():
    tokens = BuildTokens().num(1234).add().num(2124).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    expected_expr = build_binary(build_literal(1234), "add", build_literal(2124))
    assert expressions == [ExpressionStmt(expected_expr)]


def test_parse_div_precedence_right():
    tokens = BuildTokens().num(1234).add().num(2124).div().num(4).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    left_expr = build_literal(1234)
    right_expr = build_binary(build_literal(2124), "divide", build_literal(4))
    expected_expr = build_binary(left_expr, "add", right_expr)
    assert expressions == [ExpressionStmt(expected_expr)]


def test_parse_div_precedence_left():
    tokens = BuildTokens().num(1234).div().num(2124).add().num(4).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    left_expr = build_binary(build_literal(1234), "divide", build_literal(2124))
    right_expr = build_literal(4)
    expected_expr = build_binary(left_expr, "add", right_expr)
    assert expressions == [ExpressionStmt(expected_expr)]


def test_multiple_expressions():
    tokens = BuildTokens().num(1234).add().num(4).end_expr().num(10).div().num(2124).build()
    parser = setup_parser()

    expressions = parser.parse(tokens)

    first_expected_expr = build_binary(build_literal(1234), "add", build_literal(4))
    second_expected_expr = build_binary(build_literal(10), "divide", build_literal(2124))
    assert expressions == [ExpressionStmt(first_expected_expr), ExpressionStmt(second_expected_expr)]


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
