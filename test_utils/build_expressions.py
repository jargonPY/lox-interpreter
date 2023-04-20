from typing import Self
from data_types.token_type import TokenType
from data_types.lexical_token import Token
from data_types.expr import *
from data_types.stmt import *


class ExprBuilder:
    def binary(self, left: Expr, operator: Token, right: Expr) -> Binary:
        return Binary(left, operator, right)

    def literal(self, value: str | float | None) -> Literal:
        return Literal(value)

    def add(self, left: Expr, right: Expr):
        return self.binary(left, Token(TokenType.PLUS, "+"), right)

    def sub(self, left: Expr, right: Expr):
        return self.binary(left, Token(TokenType.MINUS, "-"), right)

    def mul(self, left: Expr, right: Expr):
        return self.binary(left, Token(TokenType.STAR, "*"), right)

    def div(self, left: Expr, right: Expr):
        return self.binary(left, Token(TokenType.SLASH, "/"), right)

    def expr_stmt(self, expr: Expr):
        return ExpressionStmt(expr)

    def print_stmt(self, expr: Expr) -> PrintStmt:
        return PrintStmt(expr)

    def variable_stmt(self, variable_name: str, initializer: Expr | None):
        variable_token = Token(TokenType.IDENTIFIER, variable_name)
        return VarStmt(variable_token, initializer)

    def variable_expr(self, variable_name: str):
        variable_token = Token(TokenType.IDENTIFIER, variable_name)
        return Variable(variable_token)

    # def nested(self, inner_expr):
    #     return ExprBuilder(inner_expr)

    # def negate(self, expr):
    #     return self.binary(self.literal(None), Token(TokenType.MINUS, "-"), expr)

    # def group(self, inner_expr):
    #     return self.nested(inner_expr).build()
