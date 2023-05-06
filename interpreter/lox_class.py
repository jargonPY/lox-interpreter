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
