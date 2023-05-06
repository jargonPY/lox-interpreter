from typing import Dict
from interpreter.protocols import EnvironmentProtocol
from data_types.lexical_token import Token
from data_types.errors import LoxRuntimeError

"""
Defining a table for storing variables and their associated values:

There’s a Java Map in there to store the bindings. It uses bare strings for the keys,
not tokens. A token represents a unit of code at a specific place in the source text,
but when it comes to looking up variables, all identifier tokens with the same name
should refer to the same variable (ignoring scope for now). Using the raw string
ensures all of those tokens refer to the same map key.

What happens when a variable is accessed but its not defined?

- Make it a syntax error.
- Make it a runtime error.
- Allow it and return default value like 'nil'.

Lox is pretty lax, but the last option is a little too permissive to me. Making it a syntax
error—a compile-time error—seems like a smart choice. Using an undefined variable is a bug,
and the sooner you detect the mistake, the better.

The problem is that using a variable isn’t the same as referring to it. You can refer to a
variable in a chunk of code without immediately evaluating it if that chunk of code is wrapped
inside a function. If we make it a static error to mention a variable before it’s been
declared, it becomes much harder to define recursive functions.

We could accommodate single recursion—a function that calls itself—by declaring the
function’s own name before we examine its body. But that doesn’t help with mutually
recursive procedures that call each other.

Since making it a static error makes recursive declarations too difficult, we’ll defer
the error to runtime. It’s OK to refer to a variable before it’s defined as long as you
don’t evaluate the reference. That lets the program for even and odd numbers work, but
you’d get a runtime error in:

```
print a;
var a = "too late!";
```

As with type errors in the expression evaluation code, we report a runtime error by throwing
an exception. The exception contains the variable’s token so we can tell the user where in
their code they messed up.

Evaluting an uninitialized variable:

If the variable has an initializer, we evaluate it. If not, we have another choice to make.
We could have made this a syntax error in the parser by requiring an initializer. Most
languages don’t, though, so it feels a little harsh to do so in Lox.

We could make it a runtime error. We’d let you define an uninitialized variable, but if you
accessed it before assigning to it, a runtime error would occur. It’s not a bad idea, but
most dynamically typed languages don’t do that. Instead, we’ll keep it simple and say that
Lox sets a variable to nil if it isn’t explicitly initialized.

```
var a;
print a; // "nil".
```

Thus, if there isn’t an initializer, we set the value to null, which is the Java representation
of Lox’s nil value. Then we tell the environment to bind the variable to that value.
"""


class Environment:
    def __init__(self, parent_env: EnvironmentProtocol | None = None):
        self.values: Dict[str, object] = {}
        self.parent_env = parent_env  # 'None' is only used by the global environment

    def assign(self, variable_name: Token, value: object) -> None:
        """
        The key difference between assignment and definition is that assignment is not allowed
        to create a new variable. In terms of our implementation, that means it’s a runtime error
        if the key doesn’t already exist in the environment’s variable map.
        """

        if variable_name.lexeme in self.values:
            self.values[variable_name.lexeme] = value
            return

        if self.parent_env is not None:
            self.parent_env.assign(variable_name, value)
            return

        raise LoxRuntimeError(variable_name, f"Undefined variable {variable_name.lexeme}.")

    def define(self, variable_name: str, value: object) -> None:
        """
        A variable definition binds a new name to a value.

        One interesting semantic choice. When we add the key to the map, we don’t check
        to see if it’s already present. A variable statement doesn’t just define a new variable, it
        can also be used to redefine an existing variable. We could choose to make this an error instead.
        The user may not intend to redefine an existing variable. (If they did mean to, they
        probably would have used assignment, not var.)
        """
        self.values[variable_name] = value

    def get(self, variable_name: Token):
        """
        'variable_name' is of type 'Token' rather than 'str' so that the token can be passed into 'LoxRuntimeError'.
        """

        if variable_name.lexeme in self.values:
            return self.values[variable_name.lexeme]

        # Tries the enclosing environment recursively
        if self.parent_env is not None:
            return self.parent_env.get(variable_name)

        raise LoxRuntimeError(variable_name, f"Undefined variable {variable_name.lexeme}.")

    def get_at(self, distance: int, variable_name: str) -> object:
        return self.ancestor(distance).values[variable_name]

    def assign_at(self, distance: int, variable_name: str, value: object) -> None:
        self.ancestor(distance).values[variable_name] = value

    def ancestor(self, distance: int) -> "Environment":
        environment = self
        for _ in range(distance):
            assert isinstance(environment.parent_env, Environment)
            environment = environment.parent_env

        return environment
