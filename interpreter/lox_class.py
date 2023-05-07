from typing import Dict, Union, TYPE_CHECKING
from interpreter.lox_callable import LoxCallable
from data_types.lexical_token import Token
from data_types.errors import LoxRuntimeError

if TYPE_CHECKING:
    from interpreter.interpreter import Interpreter
    from interpreter.lox_callable import LoxFunction

"""
An instance stores state, the class stores behavior. LoxInstance has its map of fields,
and LoxClass gets a map of methods. Even though methods are owned by the class, they
are still accessed through instances of that class.

When looking up a property on an instance, if we don’t find a matching field, we look
for a method with that name on the instance’s class. If found, we return that. This is
where the distinction between “field” and “property” becomes meaningful. When accessing
a property, you might get a field—a bit of state stored on the instance—or you could
hit a method defined on the instance’s class.
"""


class LoxClass(LoxCallable):
    def __init__(self, class_name: str, methods: Dict[str, "LoxFunction"]) -> None:
        self.class_name = class_name
        self.methods = methods

    def find_method(self, method_name: str) -> Union["LoxFunction", None]:
        if method_name in self.methods:
            return self.methods[method_name]

        return None

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        instance = LoxInstance(self)

        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def __repr__(self) -> str:
        return self.class_name


class LoxInstance:
    def __init__(self, lox_class: LoxClass) -> None:
        self.lox_class = lox_class
        self.instance_properties: Dict[object, object] = {}

    def get(self, property_name: Token):
        # A subtle point here, looking for a field first implies that fields shadow methods.
        if property_name in self.instance_properties:
            return self.instance_properties[property_name]

        method = self.lox_class.find_method(property_name.lexeme)
        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(property_name, f"Undefined property {property_name.lexeme}")

    def set(self, property_name: Token, value: object):
        self.instance_properties[property_name] = value

    def __repr__(self) -> str:
        return self.lox_class.class_name + " " + "instance"


class LoxListInstance(LoxInstance):
    def __init__(self, items: list[object]) -> None:
        self.lox_list = items
        self.methods = {"append": LoxListAppendItem, "delete": LoxListDeleteItem}

    def get(self, property_name: Token):
        if property_name.lexeme in self.methods:
            return self.methods[property_name.lexeme](self)

        raise LoxRuntimeError(property_name, f"Undefined property {property_name.lexeme}")

    def get_item(self, index: object):
        """
        Used by 'visitLoxListIndexExpr' to get an item at a given index.
        """

        # * all Lox number literals are converted to Python floats
        if not isinstance(index, float):
            return None
            # raise LoxRuntimeError(lox_list, f"TypeError list indices must be integers not {type(index)}")

        if len(self.lox_list) <= index:
            return None
            # raise LoxRuntimeError(lox_list, "IndexError list index out of range")

        return self.lox_list[int(index)]

    def __repr__(self) -> str:
        return repr(self.lox_list)


class LoxListAppendItem(LoxCallable):
    def __init__(self, lox_list_instance: "LoxListInstance") -> None:
        self.lox_list_instance = lox_list_instance

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        self.lox_list_instance.lox_list.extend(arguments)
        return None

    def arity(self) -> int:
        # Only allows for appending one item at a time.
        return 1

    def __repr__(self) -> str:
        return "<LoxListAppendItem method append>"


class LoxListDeleteItem(LoxCallable):
    def __init__(self, lox_list_instance: "LoxListInstance") -> None:
        self.lox_list_instance = lox_list_instance

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        index = arguments[0]
        if not isinstance(index, float):
            return None
            # raise LoxRuntimeError(property_name, TypeError: the argument to pop() must be an integer.)
        if len(self.lox_list_instance.lox_list) <= index:
            # raise LoxRuntimeError(property_name, IndexError: the index provided is longer than the list.)
            return None

        removed_item = self.lox_list_instance.lox_list.pop(int(index))
        return removed_item

    def arity(self) -> int:
        # Only allows for appending one item at a time.
        return 1

    def __repr__(self) -> str:
        return "<LoxListDeleteItem method delete>"
