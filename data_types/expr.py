from abc import ABC, abstractmethod
from data_types.lexical_token import Token


class ExprVisitor(ABC):
    @abstractmethod
    def visitGroupingExpr(self, expr: "Grouping"):
        pass

    @abstractmethod
    def visitBinaryExpr(self, expr: "Binary"):
        pass

    @abstractmethod
    def visitUnaryExpr(self, expr: "Unary"):
        pass

    @abstractmethod
    def visitLiteralExpr(self, expr: "Literal"):
        pass

    @abstractmethod
    def visitVariableExpr(self, expr: "Variable"):
        pass

    @abstractmethod
    def visitAssignExpr(self, expr: "Assign"):
        pass

    @abstractmethod
    def visitLogicalExpr(self, expr: "Logical"):
        pass

    @abstractmethod
    def visitCallExpr(self, expr: "Call"):
        pass

    # @abstractmethod
    # def visitGetExpr(self, expr: "Get"):
    #     pass

    # @abstractmethod
    # def visitSetExpr(self, expr: "Set"):
    #     pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class Call(Expr):
    def __init__(self, callee: Expr, closing_paren: Token, arguments: list[Expr]) -> None:
        self.callee = callee
        # Use this token’s location when we report a runtime error caused by a function call.
        self.closing_paren = closing_paren
        self.arguments = arguments

    def accept(self, visitor: ExprVisitor):
        return visitor.visitCallExpr(self)

    def __repr__(self) -> str:
        return repr(self.callee) + "(" + repr(self.arguments) + ")"


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: ExprVisitor):
        return visitor.visitGroupingExpr(self)

    def __repr__(self) -> str:
        return "(" + self.expression.__repr__() + ")"


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visitBinaryExpr(self)

    def __repr__(self) -> str:
        return "(" + self.left.__repr__() + " " + self.operator.lexeme + " " + self.right.__repr__() + ")"


class Unary(Expr):
    def __init__(self, operator: Token, right_side: Expr) -> None:
        self.operator = operator
        self.right_side = right_side

    def accept(self, visitor: ExprVisitor):
        return visitor.visitUnaryExpr(self)

    def __repr__(self) -> str:
        return self.operator.lexeme + self.right_side.__repr__()


class Literal(Expr):
    def __init__(self, value: str | float | None) -> None:
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitLiteralExpr(self)

    def __repr__(self) -> str:
        return str(self.value)


class Variable(Expr):
    def __init__(self, variable_name: Token) -> None:
        self.variable_name = variable_name

    def accept(self, visitor: ExprVisitor):
        return visitor.visitVariableExpr(self)

    def __repr__(self) -> str:
        return self.variable_name.lexeme


class Assign(Expr):
    def __init__(self, variable_name: Token, value: Expr) -> None:
        self.variable_name = variable_name
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitAssignExpr(self)

    def __repr__(self) -> str:
        return self.variable_name.lexeme + " = " + self.value.__repr__()


class Logical(Expr):
    def __init__(self, left_side: Expr, operator: Token, right_side: Expr) -> None:
        self.operator = operator
        self.left_side = left_side
        self.right_side = right_side

    def accept(self, visitor: ExprVisitor):
        return visitor.visitLogicalExpr(self)

    def __repr__(self) -> str:
        return self.left_side.__repr__() + " " + self.operator.lexeme + " " + self.right_side.__repr__()


# class Get(Expr):
#     def __init__(self, name: Token, obj: Expr) -> None:
#         self.name = name
#         self.obj = obj

#     def accept(self, visitor: ExprVisitor):
#         return visitor.visitGetExpr(self)

#     def __repr__(self) -> str:
#         return self.name.lexeme + " = " + self.obj.__repr__()


# class Set(Expr):
#     def __init__(self, name: Token, obj: Expr, value: Expr) -> None:
#         self.name = name
#         self.obj = obj
#         self.value = value

#     def accept(self, visitor: ExprVisitor):
#         return visitor.visitSetExpr(self)

#     def __repr__(self) -> str:
#         return self.name.lexeme + " = " + self.value.__repr__()  # todo change this representation
