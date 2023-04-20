---
id: 6osiks23z1leur017n07ef0
title: Variables
desc: ''
updated: 1681974210601
created: 1681973518478
---

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
