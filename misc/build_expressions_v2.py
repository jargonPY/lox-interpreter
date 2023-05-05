from typing import Self
from data_types.token_type import TokenType
from data_types.lexical_token import Token
from data_types.expr import Expr, Binary, Literal


class ExprBuilder:
    def __init__(self, expr=None):
        self.expr = expr

    def build(self):
        return self.expr

    def binary(self, left, operator, right):
        expr = Binary(left, operator, right)
        return expr

    def literal(self, value):
        expr = Literal(value)
        return expr

    def nested(self, inner_expr):
        return ExprBuilder(inner_expr)

    def add(self, left, right):
        return self.binary(left, Token(TokenType.PLUS, "+"), right)

    def sub(self, left, right):
        return self.binary(left, Token(TokenType.MINUS, "-"), right)

    def mul(self, left, right):
        return self.binary(left, Token(TokenType.STAR, "*"), right)

    def div(self, left, right):
        return self.binary(left, Token(TokenType.SLASH, "/"), right)

    # def negate(self, expr):
    #     return self.binary(self.literal(None), Token(TokenType.MINUS, "-"), expr)

    # def group(self, inner_expr):
    #     return self.nested(inner_expr).build()


builder = ExprBuilder()
expr = builder.add(
    builder.literal(1),
    builder.sub(
        builder.literal(2), builder.mul(builder.literal(3), builder.div(builder.literal(4), builder.literal(5)))
    ),
)
print(expr)
