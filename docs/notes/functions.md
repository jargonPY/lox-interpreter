---
id: urtmpm5ntdyrif2m6jyxt41
title: Functions
desc: ''
updated: 1681810024741
created: 1681390179249
---

### Function Grammar

**program** -> declaration ;

**declaration** -> varDecl | funDecl | statement ;

**funDecl** -> "fun" IDENTIFIER "(" parameters? ")" block ;

- The function is a name followed by the parenthesized parameter list ('?' represents zero or more) and the body.

**parameters** -> IDENTIFIER ( "," IDENTIFIER )\* ;

> A named function declaration isn’t really a single primitive operation. It’s syntactic sugar for two distinct steps: (1) creating a new function object, and (2) binding a new variable to it. If Lox had syntax for anonymous functions, we wouldn’t need function declaration statements. You could just do:

> ```
> var add = fun (a, b) {
>   print a + b;
> };
> ```

> However, since named functions are the common case, I went ahead and gave Lox nice syntax for them. (See Challenges section for more)

### Native Functions

[[../interpreter/lox_callable.py]]

Native function are functions that the interpreter exposes to the user but that are implemented in the host language, not in the language being implemented (in this case in Python rather than in Lox).

Since these functions are called while the users program is running, they form part of the implementation's runtime.

- Also called primitives, external functions, or foreign functions.

> The native functions your implementation provides are key. They provide access to the fundamental services that all programs are defined in terms of. If you don’t provide native functions to access the file system, a user’s going to have a hell of a time writing a program that reads and displays a file.

### Function Declarations

### Function Objects

We’ve got some syntax parsed so usually we’re ready to interpret, but first we need to think about how to represent a Lox function in Java. We need to keep track of the parameters so that we can bind them to argument values when the function is called. And, of course, we need to keep the code for the body of the function so that we can execute it.

That’s basically what the Stmt.Function class is. Could we just use that? Almost, but not quite. We also need a class that implements LoxCallable so that we can call it. We don’t want the runtime phase of the interpreter to bleed into the front end’s syntax classes so we don’t want Stmt.Function itself to implement that. Instead, we wrap it in a new class.

Parameters are core to functions, especially the fact that a function encapsulates its parameters—no other code outside of the function can see them. This means each function gets its own environment where it stores those variables.

Further, this environment must be created dynamically. Each function call gets its own environment. Otherwise, recursion would break. If there are multiple calls to the same function in play at the same time, each needs its own environment, even though they are all calls to the same function.

**We create a new environment at each call, not at the function declaration.**

_LoxFunction:_
[[../interpreter/lox_callable.py]]
At the beginning of the call, it creates a new environment. Then it walks the
parameter and argument lists in lockstep. For each pair, it creates a new variable
with the parameter’s name and binds it to the argument’s value.

Once the body of the function has finished executing, executeBlock() discards that
function-local environment and restores the previous one that was active back at
the callsite.

Note when we bind the parameters, we assume the parameter and argument lists have
the same length. This is safe because visitCallExpr() checks the arity before
calling call().

### Interpreting Function Declarations

_visitFunctionStmt:_
[[../interpreter/interpreter.py]]

Similar to how we interpret other literal expressions. We take a function
syntax node — a compile-time representation of the function — and convert it to
its runtime representation. Here, that’s a LoxFunction that wraps the syntax node.

Function declarations are different from other literal nodes in that the declaration
also binds the resulting object to a new variable. So, after creating the LoxFunction,
we create a new binding in the current environment and store a reference to it there.

> Note the difference between **compile-time representation and the runtime representation**.

### Return Statements

The return value is optional to support exiting early from a function that doesn’t return a useful value. In statically typed languages, “void” functions don’t return a value and non-void ones do. Since Lox is dynamically typed, there are no true void functions. The compiler has no way of preventing you from taking the result value of a call to a function that doesn’t contain a return statement.

This means every Lox function must return something, even if it contains no return statements at all. We use nil for this, which is why LoxFunction’s implementation of call() returns null at the end. In that same vein, if you omit the value in a return statement, we simply treat it as equivalent to:

### Returning From Calls

Interpreting a return statement is tricky. You can return from anywhere within the body of a function, even deeply nested inside other statements. When the return is executed, the interpreter needs to jump all the way out of whatever context it’s currently in and cause the function call to complete, like some kind of jacked up control flow construct.

When we execute a return statement, we’ll use an exception to unwind the interpreter past the visit methods of all of the containing statements back to the code that began executing the body.

### Challenges

1. Lox’s function declaration syntax performs two independent operations. It creates a function and also binds it to a name. Add support for anonymous functions or lambdas — an expression syntax that creates a function without binding it to a name.

```

fun thrice(fn) {
for (var i = 1; i <= 3; i = i + 1) {
fn(i);
}
}

thrice(fun (a) {
print a;
});
// "1".
// "2".
// "3".

```

How do you handle the tricky case of an anonymous function expression occurring in an expression statement: `fun () {};`

2. Is this program valid?

```

fun scope(a) {
var a = "local";
}

```

In other words, are a function’s parameters in the same scope as its local variables, or in an outer scope? What does Lox do? What about other languages you are familiar with? What do you think a language should do?

```

```
