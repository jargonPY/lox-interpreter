---
id: zk4kzoqazl87gm6lqspl0l8
title: Resolving and Binding
desc: ''
updated: 1681893053927
created: 1681744750422
---

### Static Scope

Lox uses **lexical scoping**. This means you can figure out which declaration a variable refers to just by reading the text of the program.

A _variable usage_ (variable expressions or assignments) refers to the _preceding_ (before in the program text) declaration with the same name in the innermost scope that encloses the expression where that variable is used.

- Since there is no mention of runtime behaviour, it implies that a variable expression _always refers to the same declaration through the entire execution of the program_.

```
var a = "global";

{
  fun showA() {
    print a;
  }

  showA();
  var a = "block";
  showA();
}
```

This program **never reassigns** any variable and contains only a single `print` statement. Yet, somehow, that `print` statement for a never-assigned variable prints two different values at **different points in time**.

### Scope and Mutable Environments

But in our implementation, environments do act like the entire block is one scope, just a scope that changes over time. Closures do not like that. When a function is declared, it captures a reference to the current environment. The function should capture a frozen snapshot of the environment as it existed at the moment the function was declared. But instead, in the Java code, it has a reference to the actual mutable environment object. When a variable is later declared in the scope that environment corresponds to, the closure sees the new variable, even though the declaration does not precede the function.

### Semantic Analysis
