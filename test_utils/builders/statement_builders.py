from data_types.expr import *
from data_types.stmt import *
from data_types.token_type import TokenType


def build_variable_declaration(
    variable_name="x",
    initializer: Expr | None = None,
) -> VarStmt:
    variable_name_token = Token(TokenType.IDENTIFIER, variable_name)
    return VarStmt(variable_name_token, initializer)


def build_print(expr: Expr) -> PrintStmt:
    return PrintStmt(expr)


def build_while(condition: Expr, body: Stmt) -> WhileStmt:
    return WhileStmt(condition, body)


def build_if(condition: Expr, then_branch: Stmt, else_branch: Stmt | None) -> IfStmt:
    return IfStmt(condition, then_branch, else_branch)


def build_block(statements: list[Stmt]) -> BlockStmt:
    return BlockStmt(statements)
