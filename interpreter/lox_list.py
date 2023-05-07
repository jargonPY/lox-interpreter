from typing import TYPE_CHECKING
from interpreter.lox_callable import LoxCallable
from data_types.lexical_token import Token
from data_types.errors import LoxRuntimeError
from interpreter.lox_class import LoxInstance

if TYPE_CHECKING:
    from interpreter.interpreter import Interpreter

# ? Why does "LoxListInstance" inherit from "LoxInstance" ?
# ? Is it necessary for type checking in the interperter ?

# * Yes, the interperter checks to make sure the object is of type "LoxInstance" in "visitGetExpr" and "visitSetExpr".
# * So inheritance here is used only for proper typing rather than sharing functionality.

"""
A potential fix it to follow the same pattern used for 'LoxCallable' and 'LoxFunction'.

'LoxCallable' is an ABC that is used as a type for any callable object including:

- User defined functions.
- Native functions.
- Classes.

'LoxFunction' is specifically a runtime wrapper for user defined functions. Its not used
for native functions.
"""


class LoxListInstance(LoxInstance):
    def __init__(self, items: list[object]) -> None:
        self.lox_list = items
        self.methods = {"append": LoxListAppendItem, "delete": LoxListDeleteItem}

    def get(self, property_name: Token):
        if property_name.lexeme in self.methods:
            return self.methods[property_name.lexeme](self)

        raise LoxRuntimeError(property_name, f"Undefined property {property_name.lexeme}")

    def set(self, property_name: Token, value: object):
        raise LoxRuntimeError(property_name, "AttributeError: Can not set properties on LoxList object.")

    def get_item(self, index: object):
        """
        Used by 'visitLoxListIndexExpr' to get an item at a given index.
        """

        index = self.validate_index(index)
        return self.lox_list[index]

    def validate_index(self, index: object) -> int:
        """
        Raises an error if the index is invalid. Casts the index to 'int' and return it otherwise.
        """

        # * all Lox number literals are converted to Python floats
        if not isinstance(index, float):
            raise RuntimeError()
            # raise LoxRuntimeError(lox_list, f"TypeError list indices must be integers not {type(index)}")

        if len(self.lox_list) <= index:
            raise RuntimeError()
            # raise LoxRuntimeError(lox_list, "IndexError list index out of range")

        return int(index)

    def __repr__(self) -> str:
        return repr(self.lox_list)


class LoxListAppendItem(LoxCallable):
    def __init__(self, instance: "LoxListInstance") -> None:
        self.instance = instance

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        self.instance.lox_list.extend(arguments)
        return None

    def arity(self) -> int:
        # Only allows for appending one item at a time.
        return 1

    def __repr__(self) -> str:
        return "<LoxListAppendItem method append>"


class LoxListDeleteItem(LoxCallable):
    def __init__(self, instance: "LoxListInstance") -> None:
        self.instance = instance

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        index = self.instance.validate_index(arguments[0])
        removed_item = self.instance.lox_list.pop(index)
        return removed_item

    def arity(self) -> int:
        return 1

    def __repr__(self) -> str:
        return "<LoxListDeleteItem method delete>"
