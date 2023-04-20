---
id: tpve9gtmqt5ihn27czubls5
title: Statements
desc: ''
updated: 1681832080748
created: 1681810104366
---

**Statement** - an action / side-effect.

**Expression** - evaluates to a value.

An expression can be used within a statement to provide a value or condition for the statement to act upon.

**Expression statement** - lets you place an expression where a statement is expected. They exist to evaluate expressions that have side effects.

**Q: Aren't expressions then a "subset" of statements (at least in the way we define the grammar)?**

It is since statements can contain expressions but expressions can never contain statements.

### Grammar

**program** -> declaration ;

**declaration** -> varDecl | funDecl | statement ;

**statement** -> exprStmt | ifStmt | whileStmt | forStmt | printStmt | blockStmt | returnStmt ;

**exprStmt** -> expression ";" ;

- Note that an exprStmt is an expression followed by a semicolon.

### Declarations

Declarations are statements but they are different from other statements, that's because the grammar restricts where some kinds of statements are allowed.

For example:

```
if (monday) print "Ugh, already?";            // This is allowed.

if (monday) var beverage = "espresso";        // This is not allowed.
```

We could allow the latter, but it’s confusing. What is the scope of that beverage variable? Does it persist after the if statement? If so, what is its value on days other than Monday? Does the variable exist at all on those days?

Code like this is weird, so C, Java, and friends all disallow it. It’s as if there are two levels of “precedence” for statements. Some places where a statement is allowed—like inside a block or at the top level—allow any kind of statement, including declarations. Others allow only the “higher” precedence statements that don’t declare names.

### Difference between Expression and Statement

https://stackoverflow.com/questions/19132/expression-versus-statement

In the earliest general-purpose programming languages, like FORTRAN, the distinction was crystal-clear. In FORTRAN, a statement was one unit of execution, a thing that you did. The only reason it wasn't called a "line" was because sometimes it spanned multiple lines. An expression on its own couldn't do anything... you had to assign it to a variable.

- _From the beginning a program was composed of a series of statements. Expressions were just a part of a larger statement._
