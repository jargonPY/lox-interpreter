from data_types.expr import *
from data_types.token_type import TokenType


def build_literal(value: str | float | None) -> Literal:
    return Literal(value)


def build_variable(variable_name="x") -> Variable:
    variable_name_token = Token(TokenType.IDENTIFIER, variable_name)
    return Variable(variable_name_token)


def build_assign(variable_name: str, value: Expr) -> Assign:
    variable_name_token = Token(TokenType.IDENTIFIER, variable_name)
    return Assign(variable_name_token, value)


def build_binary(left: Expr, operator, right: Expr) -> Binary:
    OPERATOR_TOKENS = {
        "equal": Token(TokenType.EQUAL_EQUAL, "=="),
        "not_equal": Token(TokenType.BANG_EQUAL, "!="),
        "add": Token(TokenType.PLUS, "+"),
        "subtract": Token(TokenType.MINUS, "-"),
        "multiply": Token(TokenType.STAR, "*"),
        "divide": Token(TokenType.SLASH, "/"),
    }

    operator_token = OPERATOR_TOKENS[operator]
    return Binary(left, operator_token, right)


def build_logical(left: Expr, operator, right: Expr) -> Logical:
    OPERATOR_TOKENS = {
        "or": Token(TokenType.OR, "or"),
        "and": Token(TokenType.AND, "and"),
    }

    operator_token = OPERATOR_TOKENS[operator]
    return Logical(left, operator_token, right)


def build_function_call(callee: Expr, arguments: list[Expr]) -> Call:
    return Call(callee, Token(TokenType.RIGHT_PAREN, ")"), arguments)
