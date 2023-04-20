---
id: s77w0adb1tqjpiwlderg7hi
title: Parser
desc: ''
updated: 1681301745065
created: 1681299646588
---

### `ForStmt` Tests

_What is being tested?_

Need to test that a sequence of tokens that represent a `for` statement is parsed correctly.

_What is the input / output?_

input: a sequence of tokens.
output: a `ForStmt` object.

To test this we need to construct two objects:

1. The sequence of tokens.
2. An object to match the returned value against. This can be a manually build `ForStmt` or a string representation of the object, in essence it can any representation of "equality" we choose.

`ForStmtTokenBuilder` is a helper class for constructing a sequence of tokens that represent a `for` statement. The same can be achieved by using `BuildTokens` directly (and in fact that is what `ForStmtTokenBuilder` uses) but for readablility purposes it helps break down the complex statement into its components (ex. `initializer`, `condition` etc.).
