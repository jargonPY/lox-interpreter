from typing import Self, Dict

# from data_types.token_type import TokenType
# from data_types.lexical_token import Token
# from data_types.expr import Expr, Binary, Literal

"""
In this implementation, we use a stack to keep track of the expressions and operators.
The 'add_literal', 'add_binary', 'add_unary', and 'group' methods add a new expression to the
stack, either by creating a new instance or wrapping an existing one. The 'add_operator'
method adds an operator to the stack, but first checks the precedence of the operator
against the operators already on the stack and adds any higher-precedence operators first.
"""


class TokenTypeClass:
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"


PRECEDENCE: Dict[str, int] = {
    TokenTypeClass.PLUS: 1,
    TokenTypeClass.MINUS: 1,
    TokenTypeClass.STAR: 2,
    TokenTypeClass.SLASH: 2,
}


class Token:
    def __init__(self, token_type: str, lexeme: str, literal=None, line: int = 1):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line


class Expr:
    def __repr__(self):
        pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.operator.lexeme} {self.right})"


class Literal(Expr):
    def __init__(self, value: str | float | None) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)


class Unary(Expr):
    def __init__(self, operator: Token, operand: Expr) -> None:
        self.operator = operator
        self.operand = operand

    def __repr__(self) -> str:
        return f"({self.operator.lexeme} {self.operand})"


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f"(group {self.expression})"


class ExprBuilder:
    def __init__(self, expr=None):
        self.expr = expr or []

    def build(self):
        return self.expr[-1]

    def add_literal(self, value):
        self.expr.append(Literal(value))
        return self

    def add_binary(self, operator):
        right = self.expr.pop()
        left = self.expr.pop()
        self.expr.append(Binary(left, operator, right))
        return self

    # def add_unary(self, operator):
    #     operand = self.expr.pop()
    #     self.expr.append(Unary(operator, operand))
    #     return self

    # def group(self):
    #     self.expr.append(Grouping(self.expr.pop()))
    #     return self

    def add_operator(self, operator):
        precedence = PRECEDENCE[operator.token_type]
        while (
            self.expr
            and isinstance(self.expr[-1], Expr)
            and precedence <= PRECEDENCE.get(self.expr[-1].operator.token_type, 0)
        ):
            self.add_binary(self.expr.pop().operator)
        self.expr.append(operator)
        return self


builder = ExprBuilder()
expr = (
    builder.add_literal(1)
    .add_operator(Token(TokenTypeClass.PLUS, "+"))
    .add_literal(2)
    .add_operator(Token(TokenTypeClass.STAR, "*"))
    # .group()
    .add_literal(3)
    # .add_unary(Token(TokenType.MINUS, "-"))
    .build()
)
print(expr)
