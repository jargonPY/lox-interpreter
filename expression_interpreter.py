from typing import Protocol
from data_types.expr import *
from data_types.stmt import *
from data_types.token_type import TokenType
from data_types.errors import LoxRuntimeError
from interpreter.helpers import is_operand_of_type, stringify

"""
This is the initial version of the interpreter that evaluates a single expression at a time and returns the result.
"""


class ErrorReporter(Protocol):
    def set_runtime_error(self, error: LoxRuntimeError) -> None:
        ...


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter

    def interpret(self, expression: Expr) -> object:
        value = None
        try:
            value = self.evaluate(expression)
            print("\nInterpret Result: ", stringify(value))
        except LoxRuntimeError as e:
            print("\nInterpret Error: ", e)
            self.error_reporter.set_runtime_error(e)
        return value

    def evaluate(self, expr: Expr) -> object:
        """
        Sends the expression back into the interpreter’s visitor implementation.
        """
        return expr.accept(self)

    def visitBinaryExpr(self, expr: "Binary") -> object:
        """
        Dynamically checks the types of the operands and casts them.

        If we were to assume the operands are a certain type and the casting failed
        we would get a Python exception rather than a LoxRuntimeError.
        """
        left_operand = self.evaluate(expr.left)
        right_operand = self.evaluate(expr.right)

        # * By handling the "PLUS" case first we can just have one type check rather than every if having a type check.
        if expr.operator.type == TokenType.PLUS:
            if isinstance(left_operand, float) and isinstance(right_operand, float):
                return left_operand + right_operand

            if isinstance(left_operand, str) and isinstance(right_operand, str):
                return left_operand + right_operand

            raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")

        if is_operand_of_type(left_operand, expr.operator) and is_operand_of_type(right_operand, expr.operator):
            if expr.operator.type == TokenType.MINUS:
                return left_operand - right_operand

            if expr.operator.type == TokenType.STAR:
                return left_operand * right_operand

            if expr.operator.type == TokenType.SLASH:
                if right_operand == 0:
                    raise LoxRuntimeError(expr.operator, "ZeroDivisionError: Can not divide by zero.")

                return left_operand / right_operand

        # Should be unreachable
        raise LoxRuntimeError(expr.operator, "Operator is not a valid binary expression.")

    # todo implement method properly
    def visitUnaryExpr(self, expr: "Unary") -> object:
        return expr.operator

    # todo implement method properly
    def visitGroupingExpr(self, expr: "Grouping") -> object:
        return expr.expression

    def visitLiteralExpr(self, expr: "Literal") -> object:
        return expr.value
