from abc import ABC, abstractmethod
from data_types.expr import Expr, Variable
from data_types.lexical_token import Token


class StmtVisitor(ABC):
    @abstractmethod
    def visitExpressionStmt(self, stmt: "ExpressionStmt"):
        pass

    @abstractmethod
    def visitPrintStmt(self, stmt: "PrintStmt"):
        pass

    @abstractmethod
    def visitIfStmt(self, stmt: "IfStmt"):
        pass

    @abstractmethod
    def visitWhileStmt(self, stmt: "WhileStmt"):
        pass

    @abstractmethod
    def visitVarStmt(self, stmt: "VarStmt"):
        pass

    @abstractmethod
    def visitBlockStmt(self, stmt: "BlockStmt"):
        pass

    @abstractmethod
    def visitFunctionStmt(self, stmt: "FunctionStmt"):
        pass

    @abstractmethod
    def visitReturnStmt(self, stmt: "ReturnStmt"):
        pass

    # @abstractmethod
    # def visitClassStmt(self, stmt: "ClassStmt"):
    #     pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class ExpressionStmt(Stmt):
    def __init__(self, expr: Expr) -> None:
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visitExpressionStmt(self)

    def __repr__(self) -> str:
        return repr(self.expression)


class PrintStmt(Stmt):
    def __init__(self, expr: Expr) -> None:
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visitPrintStmt(self)

    def __repr__(self) -> str:
        return "print" + " " + repr(self.expression) + ";"


class VarStmt(Stmt):
    def __init__(self, variable_name: Token, initializer: Expr | None) -> None:
        self.variable_name = variable_name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visitVarStmt(self)

    def __repr__(self) -> str:
        return f"var {self.variable_name.lexeme} = {self.initializer.__repr__()}"


class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self.statements = statements

    def accept(self, visitor: StmtVisitor):
        return visitor.visitBlockStmt(self)

    def __repr__(self) -> str:
        return "{" + f"{[repr(statement) for statement in self.statements]}" + "}"
        # return repr([repr(statement) for statement in self.statements])


class IfStmt(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor):
        return visitor.visitIfStmt(self)

    def __repr__(self) -> str:
        return repr(self.condition)


class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visitWhileStmt(self)

    def __repr__(self) -> str:
        return "while" + " (" + repr(self.condition) + ") " + repr(self.body)


class FunctionStmt(Stmt):
    def __init__(self, func_name: Token, params: list[Token], body: list[Stmt]) -> None:
        self.func_name = func_name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visitFunctionStmt(self)

    def __repr__(self) -> str:
        return "fun" + " " + repr(self.func_name) + "(" + repr(self.params) + ")"


class ReturnStmt(Stmt):
    def __init__(self, keyword: Token, value: Expr | None) -> None:
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor):
        return visitor.visitReturnStmt(self)

    def __repr__(self) -> str:
        return "return" + " " + repr(self.value)


# class ClassStmt(Stmt):
#     def __init__(self, name: Token, super_class: Variable, methods: list[FunctionStmt]) -> None:
#         self.name = name
#         self.super_class = super_class
#         self.methods = methods

#     def accept(self, visitor: StmtVisitor):
#         return visitor.visitClassStmt(self)

#     def __repr__(self) -> str:
#         return self.name.lexeme
