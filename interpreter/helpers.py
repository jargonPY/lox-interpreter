from typing import TypeVar, TypeGuard
from data_types.errors import LoxRuntimeError
from data_types.lexical_token import Token

T = TypeVar("T")


def is_operand_of_type_float(
    operand: T, operator: Token, message: str = "Operands must be numbers."
) -> TypeGuard[float]:
    """
    User-defined type guard.

    Takes a variable as input and returns True if the variable is of type 'float', throws a RuntimeError otherwise.

    operator: used to track the token that identifies where in the user’s code the runtime error came from.
    operand: the value whose type is being checked.
    """
    if isinstance(operand, float):
        return True

    raise LoxRuntimeError(operator, message)


def stringify(value: object) -> str:
    """
    A helper method for converting Python values into Lox values for displaying.

    This method crosses the membrane between the user’s view of Lox objects and
    their internal representation in Python.
    """

    # ? Why can't we use "isinstance(value, None)"?
    if value is None:
        return "nil"

    # Lox uses "float" even for "int" values. In that case, it should print without a decimal point.
    if isinstance(value, float):
        text = str(value)
        if text.endswith(".0"):
            text = text.split(".")[0]
        return text

    return str(value)


def is_equal(a: object, b: object) -> bool:
    if a is None and b is None:
        return True

    if a is None:
        return False

    return a == b
