from typing import Protocol
from data_types.expr import *
from data_types.stmt import *
from data_types.token_type import TokenType
from data_types.lexical_token import Token
from data_types.errors import LoxRuntimeError, ReturnException
from data_types.error_messages import *
from interpreter.protocols import EnvironmentProtocol
from interpreter.environment import Environment
from interpreter.helpers import is_operand_of_type_float, stringify, is_equal
from interpreter.lox_callable import LoxCallable, LoxFunction, Clock
from interpreter.lox_class import LoxClass, LoxInstance
from interpreter.lox_list import LoxListInstance
from resolver.resolver import ResolvedVars

"""
Runtime Errors:

We could print a runtime error and then abort the process and exit the application
entirely (that is what compilers do, although its not in the runtime).

While a runtime error needs to stop evaluating the expression, it shouldn’t kill
the interpreter. If a user is running the REPL and has a typo in a line of code,
they should still be able to keep the session going and enter more code after that.
"""

"""
The REPL no longer supports entering a single expression and automatically printing its
result value. That’s a drag. Add support to the REPL to let users type in both statements
and expressions. If they enter a statement, execute it. If they enter an expression,
evaluate it and display the result value.
"""


class ErrorReporter(Protocol):
    def set_runtime_error(self, error: LoxRuntimeError) -> None:
        ...


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, environment: EnvironmentProtocol, error_reporter: ErrorReporter) -> None:
        self.globals = environment  # Holds a fixed reference to the outermost global environment.
        self.environment = self.globals  # Changes as we enter and exit local scopes. It tracks the current environment.
        self.error_reporter = error_reporter

        self.resolved_local_vars: ResolvedVars = {}

        # When we instantiate an Interpreter, we stuff the native function in that global scope.
        # todo move defining native function and setting up the global environment into a different location.
        self.globals.define("clock", Clock())

    def is_truthy(self, obj: object) -> bool:
        """
        What happens when you use something other than true or false in a logic operation like ! or
        any other place where a Boolean is expected?

        One option is to make it an error if we don't want implicit conversions, but most
        dynamically typed languages don't do that. Instead, they take the universe of values
        of all types and partition them into two sets, one of which they define to be “true”, or
        “truthful”, or (my favorite) “truthy”, and the rest which are “false” or “falsey”. This
        partitioning is somewhat arbitrary.

        Lox follows Ruby’s simple rule: false and nil are falsey, and everything else is truthy.
        """
        if obj is None:
            return False

        if isinstance(obj, bool):
            return obj

        return True

    def interpret(self, statements: list[Stmt], resolved_local_vars: ResolvedVars) -> None:
        """
        Accepts a list of statements — in other words, a program.
        """

        self.resolved_local_vars = resolved_local_vars
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            print("\nInterpret Error: ", e)
            self.error_reporter.set_runtime_error(e)

    def executeBlock(self, statements: list[Stmt], environment: EnvironmentProtocol):
        """
        Executes a list of statements in the context of a given environment.

        * Manually changing and restoring a mutable environment field feels inelegant.
          Another classic approach is to explicitly pass the environment as a parameter
          to each visit method. To “change” the environment, you pass a different one as
          you recurse down the tree. You don’t have to restore the old one, since the new
          one lives on the Java stack and is implicitly discarded when the interpreter
          returns from the block’s visit method.
        """
        prev_env = self.environment

        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        # * Can't have an except statement here since it would catch the ReturnException and not pass it through to LoxFunction
        # except Exception as e:
        #     print("Execute Block Error: ", e)
        #     pass
        finally:
            self.environment = prev_env

    def lookup_variable(self, variable_name: Token, expr: Expr) -> object:
        if expr in self.resolved_local_vars:
            distance = self.resolved_local_vars[expr]
            return self.environment.get_at(distance, variable_name.lexeme)

        return self.globals.get(variable_name)

    def execute(self, stmt: Stmt) -> None:
        """
        Sends the statement back into the interpreter’s visitor implementation.

        This method is the statement analogue to the 'evaluate()' method for expressions.
        """
        stmt.accept(self)

    def evaluate(self, expr: Expr) -> object:
        """
        Sends the expression back into the interpreter’s visitor implementation.
        """
        return expr.accept(self)

    def visitVarStmt(self, stmt: "VarStmt") -> None:
        value = None

        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.variable_name.lexeme, value)

    def visitClassStmt(self, stmt: "ClassStmt") -> None:
        """
        The two-stage variable binding process (defining and then assigning) allows references
        to the class inside its own methods.
        """
        self.environment.define(stmt.name.lexeme, None)

        # Convert each method declaration into a LoxFunction object (the runtime representation).
        methods = {}
        for method in stmt.methods:
            lox_function = LoxFunction(method, self.environment)
            methods[method.func_name.lexeme] = lox_function

        lox_class = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, lox_class)

    def visitFunctionStmt(self, stmt: "FunctionStmt") -> None:
        """
        Similar to how we interpret other literal expressions. We take a function
        syntax node — a compile-time representation of the function — and convert it to
        its runtime representation. Here, that’s a LoxFunction that wraps the syntax node.

        Function declarations are different from other literal nodes in that the declaration
        also binds the resulting object to a new variable. So, after creating the LoxFunction,
        we create a new binding in the current environment and store a reference to it there.
        """

        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.func_name.lexeme, function)

    def visitReturnStmt(self, stmt: "ReturnStmt") -> None:
        """
        If there is a return value, we evaluate it, otherwise, we use nil. Then we take that
        value and wrap it in a custom exception class and throw it.
        """

        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise ReturnException(value)

    def visitCallExpr(self, expr: "Call") -> object:
        # Evaluate the expression for the callee
        callee = self.evaluate(expr.callee)

        # Evaluate each of the argument expressions
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        # Ensure that the 'callee' is a callable object
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.closing_paren, "Can only call functions and classes.")

        # Before invoking the callable, we check to see if the argument list’s length matches the callable’s arity
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.closing_paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visitGetExpr(self, expr: "Get") -> object:
        obj = self.evaluate(expr.obj)

        if isinstance(obj, LoxInstance):
            return obj.get(expr.property_name)

        raise LoxRuntimeError(expr.property_name, "Only class instances have properties.")

    def visitSetExpr(self, expr: "Set") -> object:
        obj = self.evaluate(expr.obj)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.property_name, "Only class instances have properties.")

        value = self.evaluate(expr.value)
        obj.set(expr.property_name, value)
        return value

    def visitThisExpr(self, expr: "This") -> object:
        return self.lookup_variable(expr.keyword, expr)

    def visitVariableExpr(self, expr: "Variable") -> object:
        # return self.environment.get(expr.variable_name)
        # * Replace the above query of the environment with the variable resolution query
        return self.lookup_variable(expr.variable_name, expr)

    def visitAssignExpr(self, expr: "Assign") -> object:
        """
        Returns the assigned value. That’s because assignment is an expression that can be
        nested inside other expressions.

        var a = 1;
        print a = 2; // "2"
        """
        value = self.evaluate(expr.value)
        # self.environment.assign(expr.variable_name, value)
        # * Replace the above query of the environment with the variable resolution query
        if expr in self.resolved_local_vars:
            distance = self.resolved_local_vars[expr]
            self.environment.assign_at(distance, expr.variable_name.lexeme, value)
        else:
            self.globals.assign(expr.variable_name, value)

        return value

    def visitPrintStmt(self, stmt: "PrintStmt") -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visitBlockStmt(self, stmt: "BlockStmt") -> None:
        self.executeBlock(stmt.statements, Environment(self.environment))

    def visitWhileStmt(self, stmt: "WhileStmt") -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visitIfStmt(self, stmt: "IfStmt") -> None:
        evaluate_if_branch = self.is_truthy(self.evaluate(stmt.condition))

        if evaluate_if_branch:
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visitExpressionStmt(self, stmt: "ExpressionStmt") -> None:
        """
        How does the result get returned to the statement (ex. var beverage = "expression";)?

        Unlike expressions, statements produce no values, so the return type of the visit methods
        is 'None', not 'object'.

        Expression statements are evaluated for their side-effect, therefore we evaluate the inner
        expression and discard the value.
        """
        self.evaluate(stmt.expression)

    def visitLogicalExpr(self, expr: "Logical") -> object:
        """
        Deciding what actual value to return. Since Lox is dynamically typed, we allow operands
        of any type and use truthiness to determine what each operand represents. We apply
        similar reasoning to the result. Instead of promising to literally return true or false,
        a logic operator merely guarantees it will return a value with appropriate truthiness.

        Example:
        print "hi" or 2; // "hi".
        print nil or "yes"; // "yes".
        """
        left_operand = self.evaluate(expr.left_side)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left_operand):
                return left_operand
        else:
            if not self.is_truthy(left_operand):
                return left_operand

        return self.evaluate(expr.right_side)

    def visitBinaryExpr(self, expr: "Binary") -> object:
        """
        Dynamically checks the types of the operands and casts them.

        If we were to assume the operands are a certain type and the casting failed
        we would get a Python exception rather than a LoxRuntimeError.
        """
        left_operand = self.evaluate(expr.left)
        right_operand = self.evaluate(expr.right)

        if expr.operator.type == TokenType.BANG_EQUAL:
            return not is_equal(left_operand, right_operand)

        if expr.operator.type == TokenType.EQUAL_EQUAL:
            return is_equal(left_operand, right_operand)

        # * By handling the "PLUS" case first we can just have one type check rather than every if having a type check.
        if expr.operator.type == TokenType.PLUS:
            if isinstance(left_operand, float) and isinstance(right_operand, float):
                return left_operand + right_operand

            if isinstance(left_operand, str) and isinstance(right_operand, str):
                return left_operand + right_operand

            raise LoxRuntimeError(expr.operator, EXPECT_TYPE_NUMBER_OR_STRING)

        # todo: change to 'are_operands_of_type_float' to check both at once otherwise might as well use 'isinstance'
        # * By checking the type here we avoid having to check the type for each case individually
        if is_operand_of_type_float(left_operand, expr.operator) and is_operand_of_type_float(
            right_operand, expr.operator
        ):
            if expr.operator.type == TokenType.MINUS:
                return left_operand - right_operand

            if expr.operator.type == TokenType.STAR:
                return left_operand * right_operand

            if expr.operator.type == TokenType.SLASH:
                if right_operand == 0:
                    raise LoxRuntimeError(expr.operator, DIVIDE_BY_ZERO_ERROR)

                return left_operand / right_operand

            if expr.operator.type == TokenType.GREATER:
                return left_operand > right_operand

            if expr.operator.type == TokenType.GREATER_EQUAL:
                return left_operand >= right_operand

            if expr.operator.type == TokenType.LESS:
                return left_operand < right_operand

            if expr.operator.type == TokenType.LESS_EQUAL:
                return left_operand <= right_operand

        # Should be unreachable
        raise LoxRuntimeError(expr.operator, INVALID_BINARY_EXPRESSION)

    def visitTernaryExpr(self, expr: "Ternary") -> object:
        condition = self.evaluate(expr.condition)

        if self.is_truthy(condition):
            return self.evaluate(expr.truthy)

        return self.evaluate(expr.falsy)

    # todo implement method properly
    def visitUnaryExpr(self, expr: "Unary") -> object:
        return expr.operator

    # todo implement method properly
    def visitGroupingExpr(self, expr: "Grouping") -> object:
        return expr.expression

    def visitLoxListIndexExpr(self, expr: "LoxListIndex") -> object:
        lox_list = self.evaluate(expr.lox_list)

        if not isinstance(lox_list, LoxListInstance):
            return None

        index = self.evaluate(expr.index)

        return lox_list.get_item(index)

    def visitLoxListExpr(self, expr: "LoxList") -> object:
        lox_list = []
        for item in expr.items:
            value = self.evaluate(item)
            lox_list.append(value)
        return LoxListInstance(lox_list)

    def visitLiteralExpr(self, expr: "Literal") -> object:
        return expr.value
