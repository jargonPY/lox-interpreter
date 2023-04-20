import time
from abc import ABC, abstractmethod
from data_types.stmt import FunctionStmt
from interpreter.protocols import EnvironmentProtocol
from interpreter.environment import Environment
from data_types.errors import ReturnException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter.interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class LoxFunction(LoxCallable):
    def __init__(self, func_declaration: FunctionStmt, closure: "EnvironmentProtocol") -> None:
        self.func_declaration = func_declaration
        # This is the environment that is active when the function is declared not when its called.
        # It represents the lexical scope surrounding the function delcaration.
        self.closure = closure

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        """
        At the beginning of the call, it creates a new environment. Then it walks the
        parameter and argument lists in lockstep. For each pair, it creates a new variable
        with the parameter’s name and binds it to the argument’s value.

        Once the body of the function has finished executing, executeBlock() discards that
        function-local environment and restores the previous one that was active back at
        the callsite.

        Note when we bind the parameters, we assume the parameter and argument lists have
        the same length. This is safe because visitCallExpr() checks the arity before
        calling call().
        """

        # environment = Environment(interpreter.globals)
        environment = Environment(self.closure)

        for i in range(len(arguments)):
            param = self.func_declaration.params[i]
            arg = arguments[i]
            environment.define(param.lexeme, arg)

        try:
            interpreter.executeBlock(self.func_declaration.body, environment)
        except ReturnException as return_value:
            return return_value.value

        return None

    def arity(self) -> int:
        return len(self.func_declaration.params)

    def __repr__(self) -> str:
        return f"<fn {self.func_declaration.func_name.lexeme}>"


class Clock(LoxCallable):
    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        return time.time()

    def arity(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "<native fn>"
