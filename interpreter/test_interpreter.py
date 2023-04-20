import pytest
from typing import Self
from interpreter.interpreter import Interpreter
from interpreter.environment import Environment
from interpreter.helpers import stringify
from data_types.lexical_token import Token
from data_types.token_type import TokenType
from data_types.expr import Expr, Binary, Literal
from data_types.errors import LoxRuntimeError
from data_types.error_messages import *
from test_utils.build_tokens import BuildTokens
from test_utils.build_expressions import ExprBuilder
from test_utils.error_reporter import TestErrorReporter
from test_utils.environment import TestEnvironment

# ! When writing test need to make sure all literal numbers are floats. When scanner scans user's input, it automatically converts to a float.

builder = ExprBuilder()


def setup_interpreter() -> Interpreter:
    return Interpreter(Environment(), TestErrorReporter())


""" ========================= Interpret Expressions Tests ========================= """


def test_evaluate_numer_literal():
    expression = builder.literal(4.0)
    interpreter = setup_interpreter()

    result = interpreter.evaluate(expression)

    assert result == 4.0


def test_evaluate_add_two_numbers():
    expression = builder.add(builder.literal(4.0), builder.literal(10.0))
    interpreter = setup_interpreter()

    result = interpreter.evaluate(expression)

    assert result == 14.0


def test_evaluate_nested_arithmetic_expression():
    left_expr = builder.add(builder.literal(20.0), builder.literal(10.0))
    right_expr = builder.div(builder.literal(20.0), builder.literal(2.0))
    expression = builder.sub(left_expr, right_expr)
    interpreter = setup_interpreter()

    result = interpreter.evaluate(expression)

    assert result == 20.0


# * Tests for Binary Expr with strings


def test_evaluate_string_literal():
    expression = builder.literal("Hello!")
    interpreter = setup_interpreter()

    result = interpreter.evaluate(expression)

    assert result == "Hello!"


def test_evaluate_string_concatenation():
    expression = builder.add(builder.literal("Hello "), builder.literal("World!"))
    interpreter = setup_interpreter()

    result = interpreter.evaluate(expression)

    assert result == "Hello World!"


""" ========================= Interpret Statements Tests ========================= """


def test_print_stmt(capsys):
    expression = builder.literal("Hello! 1234!")
    statement = builder.print_stmt(expression)
    interpreter = setup_interpreter()

    interpreter.interpret([statement])

    captured = capsys.readouterr()
    assert captured.out == "Hello! 1234!\n"


def test_print_stmt_with_binary_expression(capsys):
    expression = builder.add(builder.literal(4.0), builder.literal(10.0))
    statement = builder.print_stmt(expression)
    interpreter = setup_interpreter()

    interpreter.interpret([statement])

    captured = capsys.readouterr()
    assert captured.out == "14\n"


def test_variable_stmt_and_variable_expression(capsys):
    declare_var = builder.variable_stmt("x", builder.add(builder.literal(4.0), builder.literal(10.0)))
    print_var = builder.print_stmt(builder.variable_expr("x"))
    interpreter = setup_interpreter()

    interpreter.interpret([declare_var, print_var])

    captured = capsys.readouterr()
    assert captured.out == "14\n"


""" ========================= Error Reporting Tests ========================= """

"""
How errors are handled by the interpreter:

1. When an error is thrown the 'interpret' method returns 'None'.
2. The error is reported by calling the 'self.error_reporter.set_runtime_error(LoxRuntimeError)' method. 
"""


def test_evaluate_add_two_int_numbers():
    """
    The interpreter expects number literals to be of type 'float'.
    The interpreter dynamically checks that the numbers are 'float' type and throws an error otherwise.

    This is an internal detail of implementing Lox in Python. To the user all numbers are represented
    as Lox numbers.
    """
    expression = builder.sub(builder.literal(4), builder.literal(10))
    interpreter = setup_interpreter()

    with pytest.raises(LoxRuntimeError) as exc_info:
        interpreter.evaluate(expression)

    # * Wrapping 'exc_info.value' in 'str()' extracts the message out of the error object.
    assert str(exc_info.value) == EXPECT_TYPE_NUMBER


def test_evaluate_divide_by_zero():
    expression = builder.div(builder.literal(4.0), builder.literal(0.0))
    interpreter = setup_interpreter()

    with pytest.raises(LoxRuntimeError) as exc_info:
        interpreter.evaluate(expression)

    assert str(exc_info.value) == DIVIDE_BY_ZERO_ERROR


def test_evaluate_adding_string_to_number():
    expression = builder.add(builder.literal("Hello "), builder.literal(4.0))
    interpreter = setup_interpreter()

    with pytest.raises(LoxRuntimeError) as exc_info:
        interpreter.evaluate(expression)

    assert str(exc_info.value) == EXPECT_TYPE_NUMBER_OR_STRING


def test_evaluate_subtracting_string_from_number():
    expression = builder.sub(builder.literal("Hello "), builder.literal(4.0))
    interpreter = setup_interpreter()

    with pytest.raises(LoxRuntimeError) as exc_info:
        interpreter.evaluate(expression)

    assert str(exc_info.value) == EXPECT_TYPE_NUMBER


""" ========================= Helper Tests ========================= """


def test_stringify():
    value = 10.0

    result = stringify(value)

    assert result == "10"


def test_stringify_decimal():
    value = 10.4

    result = stringify(value)

    assert result == "10.4"
