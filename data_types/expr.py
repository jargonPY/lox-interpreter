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

    @abstractmethod
    def visitGetExpr(self, expr: "Get"):
        pass

    @abstractmethod
    def visitSetExpr(self, expr: "Set"):
        pass

    @abstractmethod
    def visitThisExpr(self, expr: "This"):
        pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Call):
            return self.callee == other.callee and self.arguments == other.arguments
        return False


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: ExprVisitor):
        return visitor.visitGroupingExpr(self)

    def __repr__(self) -> str:
        return "(" + self.expression.__repr__() + ")"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Grouping):
            return self.expression == other.expression
        return False


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visitBinaryExpr(self)

    def __repr__(self) -> str:
        return "(" + self.left.__repr__() + " " + self.operator.lexeme + " " + self.right.__repr__() + ")"

    def __eq__(self, other) -> bool:
        if isinstance(other, Binary):
            return self.left == other.left and self.operator == other.operator and self.right == other.right
        return False


class Unary(Expr):
    def __init__(self, operator: Token, right_side: Expr) -> None:
        self.operator = operator
        self.right_side = right_side

    def accept(self, visitor: ExprVisitor):
        return visitor.visitUnaryExpr(self)

    def __repr__(self) -> str:
        return self.operator.lexeme + self.right_side.__repr__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Unary):
            return self.operator == other.operator and self.right_side == other.right_side
        return False


class Literal(Expr):
    def __init__(self, value: object) -> None:
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitLiteralExpr(self)

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, Literal):
            return self.value == other.value
        return False


class Variable(Expr):
    def __init__(self, variable_name: Token) -> None:
        self.variable_name = variable_name

    def accept(self, visitor: ExprVisitor):
        return visitor.visitVariableExpr(self)

    def __repr__(self) -> str:
        return self.variable_name.lexeme

    def __hash__(self) -> int:
        return hash(self.variable_name) + id(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Variable):
            return self.variable_name == other.variable_name
        return False


class Assign(Expr):
    def __init__(self, variable_name: Token, value: Expr) -> None:
        self.variable_name = variable_name
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitAssignExpr(self)

    def __repr__(self) -> str:
        return self.variable_name.lexeme + " = " + self.value.__repr__()

    def __hash__(self) -> int:
        """
        Note that for hashable objects, the __hash__() method should be implemented consistently
        with the __eq__() method, such that two objects that compare equal have the same hash value.
        If this is not the case, unexpected behavior can occur when using the object as a key in a
        dictionary or as an element in a set.
        """
        # todo fix "__hash__" to match "__eq__", however that will cause another issue it might not match the "Variable" "__hash__", which will break the resolver.
        return hash(self.variable_name) + id(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Assign):
            return self.variable_name == other.variable_name and self.value == other.value
        return False


class Logical(Expr):
    def __init__(self, left_side: Expr, operator: Token, right_side: Expr) -> None:
        self.operator = operator
        self.left_side = left_side
        self.right_side = right_side

    def accept(self, visitor: ExprVisitor):
        return visitor.visitLogicalExpr(self)

    def __repr__(self) -> str:
        return self.left_side.__repr__() + " " + self.operator.lexeme + " " + self.right_side.__repr__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Logical):
            return (
                self.operator == other.operator
                and self.left_side == other.left_side
                and self.right_side == other.right_side
            )
        return False


class Get(Expr):
    def __init__(self, property_name: Token, obj: Expr) -> None:
        self.property_name = property_name
        self.obj = obj

    def accept(self, visitor: ExprVisitor):
        return visitor.visitGetExpr(self)

    def __repr__(self) -> str:
        return self.property_name.lexeme

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Get):
            return self.property_name == other.property_name and self.obj == other.obj
        return False


class Set(Expr):
    def __init__(self, property_name: Token, obj: Expr, value: Expr) -> None:
        self.property_name = property_name
        self.obj = obj
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitSetExpr(self)

    def __repr__(self) -> str:
        return self.property_name.lexeme + " = " + repr(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Set):
            return self.property_name == other.property_name and self.obj == other.obj and self.value == other.value
        return False


class This(Expr):
    def __init__(self, keyword: Token) -> None:
        self.keyword = keyword

    def accept(self, visitor: ExprVisitor):
        return visitor.visitThisExpr(self)

    def __repr__(self) -> str:
        return repr(self.keyword)

    def __hash__(self) -> int:
        return hash(self.keyword) + id(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, This):
            return self.keyword == other.keyword
        return False
