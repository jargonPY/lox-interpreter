---
id: 6osiks23z1leur017n07ef0
title: Variables
desc: ''
updated: 1681982066818
created: 1681973518478
---

### Variable Grammar

### Variable Declaration

```
varDecl -> "var" IDENTIFIER ( "=" expression )? ";" ;
```

Like most statements, it starts with a leading keyword. In this case, `var`. Then an identifier token for the name of the variable being declared, followed by an optional initializer expression.

AST representation:

```
VarStmt(variable_name: Token, initializer: Expr)
```

#### Variable Expression

To access a variable, we define a new kind of primary expression.

```
primary -> "true" | "false" | "nil" | NUMBER | STRING | "(" expression ")" | IDENTIFIER ;
```

That `IDENTIFIER` clause matches a single identifier token, which is understood to be the name of the variable being accessed.

AST representation:

```
Variable(variable_name: Token)
```

#### Variable Assignment

Like most C-derived languages, assignment is an expression and not a statement. As in C, it is the lowest precedence expression form.

> In some other languages, like Pascal, Python, and Go, assignment is a statement.

```
expression -> assignment ;
assignment -> IDENTIFIER "=" assignment | equality ;
```

This says an assignment is either an identifier followed by an `=` and an expression for the value, or an equality (and thus any other) expression.

AST representation:

```
Assign(variable_name: Token, initializer: Expr)
```

### Implicit Variable Declaration

Lox has distinct syntax for declaring a new variable, `var x = 10;`, and assigning to an existing one, `x = 10;`.

The other option is to collapse those to only use assignment syntax. Assigning to a non-existent variable brings it into being.

This introduces some ambiguity and the language must decide how it handles it. Specifically **how implicit variable declaration interacts with shadowing and which scope an implicitly declared variable goes to**.

Example:

```
a = 10;
{
    a = 20;
}
```

Show the `a` in the inner scope override the global one or be declared in the inner scope?

```
var a = 10;
{
    a = 20;
}

vs.

var a = 10;
{
    var a = 10;
}
```

- In Python, assignment always creates a variable in the current function’s scope, even if there is a variable with the same name declared outside of the function.

**Is implicit declaration a good idea?**

The main advantage is simplicity. There is less syntax and the user doesn't need to learn about the concept of "declaration".

However it has some problems:

- For statically typed languages its useful as you can tell the compiler the type of a variable.

- A user may intend to assign to an existing variable but may have mispelled it, the interpreter than proceeds to create a new variable.

- In Python you may want to assign to some outside variable but you can't.

Most programming languages end up adding features to address these problems (ex. Python introduced the `global` statement). This in turn adds complexity and the simplicity arugment is mostly lost.

Implicit declaration made sense in years past when most scripting languages were heavily imperative and code was pretty flat. As programmers have gotten more comfortable with deep nesting, functional programming, and closures, it’s become much more common to want access to variables in outer scopes. That makes it more likely that users will run into the tricky cases where it’s not clear whether they intend their assignment to create a new variable or reuse a surrounding one.
