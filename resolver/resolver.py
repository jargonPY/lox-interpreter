from typing import Protocol, Dict
from data_types.expr import *
from data_types.stmt import *
from data_types.lexical_token import Token
from data_types.error_messages import *
from data_types.stack import Stack
from data_types.expr import Expr

"""
Only a few kinds of nodes are interesting when it comes to resolving variables:

- A block statement introduces a new scope for the statements it contains.

- A function declaration introduces a new scope for its body and binds its parameters in that scope.

- A variable declaration adds a new variable to the current scope.

- Variable and assignment expressions need to have their variables resolved.

The rest of the nodes don’t do anything special, but we still need to implement visit methods for
them that traverse into their subtrees. Even though a + expression doesn’t itself have any
variables to resolve, either of its operands might.
"""


"""
Splitting variable declaration (VarStmt) into two seperate steps, declaring and defining, allows
us to ensure that the variable does not reference iteself or a shadowed variable.

Ex.
var a = "outer";
{
  var a = a;
}

Resolution steps:
1. "a" from the inner scope is declared as part of the scope and its value is set to "False".
2. Resolve the expression on the right hand side.
3. Since its a visitVariableExpr it can check if the variable is in the current scope and is not
   and is if it uses itself as the initializer.
"""

# The boolean value represents whether the variable has been initialized yet.
# Used to check if the variable refers to itself in the initializer.
Scope = Dict[str, bool]
ResolvedVars = Dict[Expr, int]


class ErrorReporter(Protocol):
    def set_error(self, line: int, message: str) -> None:
        ...


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter
        self.scopes: Stack[Scope] = Stack()
        self.resolved_local_vars: ResolvedVars = {}

    def declare(self, variable_name: Token) -> None:
        """
        Declaration adds the variable to the innermost scope so that it shadows any outer
        one and so that we know the variable exists. We mark it as “not ready yet” by
        binding its name to false in the scope map. The value associated with a key in the
        scope map represents whether or not we have finished resolving that variable’s
        initializer.
        """

        # * mypy doesn't see this as a type guard
        # if self.scopes.is_empty():
        #     return

        current_scope = self.scopes.peek()
        if current_scope is None:
            return

        """
        Help the user catch the following bug:
        fun bad() {
            var a = "first";
            var a = "second";
        }
        """
        if variable_name.lexeme in current_scope:
            self.error_reporter.set_error(1, "Already a variable with this name in this scope.")

        current_scope[variable_name.lexeme] = False

    def define(self, variable_name: Token) -> None:
        current_scope = self.scopes.peek()
        if current_scope is None:
            return

        current_scope[variable_name.lexeme] = True

    def resolve(self, statements: list[Stmt]) -> ResolvedVars:
        for statement in statements:
            statement.accept(self)

        return self.resolved_local_vars

    def resolve_statement(self, statement: Stmt):
        statement.accept(self)

    def resolve_expression(self, expression: Expr):
        expression.accept(self)

    def resolve_local(self, expr: Expr, variable_name: Token) -> None:
        index = self.scopes.size() - 1
        while index >= 0:
            scope = self.scopes.get(index)

            if scope is not None and variable_name.lexeme in scope:
                depth = self.scopes.size() - 1 - index
                self.resolved_local_vars[expr] = depth

            index -= 1

    def resolve_function(self, function: FunctionStmt) -> None:
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()

    def begin_scope(self) -> None:
        self.scopes.push({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def visitBlockStmt(self, stmt: "BlockStmt") -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visitFunctionStmt(self, stmt: "FunctionStmt") -> None:
        """
        Similar to visitVariableStmt(), we declare and define the name of the function in the current scope.
        Unlike variables, though, we define the name eagerly, before resolving the function’s body. This lets
        a function recursively refer to itself inside its own body.
        """

        self.declare(stmt.func_name)
        self.define(stmt.func_name)
        self.resolve_function(stmt)

    def visitVarStmt(self, stmt: "VarStmt") -> None:
        """
        Split binding into two steps, declaring then defining.
        """

        self.declare(stmt.variable_name)

        if stmt.initializer is not None:
            self.resolve_expression(stmt.initializer)

        self.define(stmt.variable_name)

    def visitVariableExpr(self, expr: "Variable") -> None:
        """
        First, we check to see if the variable is being accessed inside its own initializer.
        This is where the values in the scope map come into play. If the variable exists in
        the current scope but its value is false, that means we have declared it but not yet
        defined it. We report that error.
        """

        current_scope = self.scopes.peek()
        if current_scope is not None and current_scope.get(expr.variable_name.lexeme) == False:
            self.error_reporter.set_error(1, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.variable_name)

    def visitAssignExpr(self, expr: "Assign") -> None:
        """
        The other expression that references a variable is assignment.
        First, we resolve the expression for the assigned value in case it also contains
        references to other variables. Then we use our existing resolveLocal() method to
        resolve the variable that’s being assigned to.
        """

        self.resolve_expression(expr.value)
        self.resolve_local(expr, expr.variable_name)

    """
    That covers the interesting corners of the grammars. We handle every place where a variable is
    declared, read, or written, and every place where a scope is created or destroyed. Even though
    they aren’t affected by variable resolution, we also need visit methods for all of the other
    syntax tree nodes in order to recurse into their subtrees.
    """

    def visitExpressionStmt(self, stmt: "ExpressionStmt") -> None:
        self.resolve_expression(stmt.expression)

    def visitIfStmt(self, stmt: "IfStmt") -> None:
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.then_branch)

        if stmt.else_branch is not None:
            self.resolve_statement(stmt.else_branch)

    def visitPrintStmt(self, stmt: "PrintStmt") -> None:
        self.resolve_expression(stmt.expression)

    def visitReturnStmt(self, stmt: "ReturnStmt") -> None:
        if stmt.value is not None:
            self.resolve_expression(stmt.value)

    def visitWhileStmt(self, stmt: "WhileStmt") -> None:
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.body)

    def visitGroupingExpr(self, expr: "Grouping") -> None:
        self.resolve_expression(expr.expression)

    def visitBinaryExpr(self, expr: "Binary") -> None:
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visitUnaryExpr(self, expr: "Unary") -> None:
        self.resolve_expression(expr.right_side)

    def visitLiteralExpr(self, expr: "Literal") -> None:
        return None

    def visitLogicalExpr(self, expr: "Logical") -> None:
        self.resolve_expression(expr.left_side)
        self.resolve_expression(expr.right_side)

    def visitCallExpr(self, expr: "Call") -> None:
        self.resolve_expression(expr.callee)

        for argument in expr.arguments:
            self.resolve_expression(argument)

    def visitLoxListIndexExpr(self, expr: LoxListIndex) -> None:
        self.resolve_expression(expr.index)

    def visitLoxListExpr(self, expr: LoxList) -> None:
        for item in expr.items:
            self.resolve_expression(item)
