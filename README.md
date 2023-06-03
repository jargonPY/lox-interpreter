# lox-interpreter

This repository contains a Python implementation of an interpreter for the lox programing language described in [Crafting Interpreters](https://craftinginterpreters.com).

This implementation extends the original grammar to support:

- Ternary operators.
- List literal data type.
- Convenience methods for the list data type to support the `append` and `delete` operations.

### Using the interpreter

The interpreter can be used by either running a Lox program, by reading a `.lox` file or interactively through the terminal.

```
Example:

python lox.py                // This will start Lox as a REPL
python lox.py my_program.lox // This will read run the code in 'my_program.lox`
```

### Examples

Lox supports many of the features of traditional OOP languages. It has support for functions, classes, closures etc.

Example of using closures:

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

Example of computing the fibonacci sequence:

```
fun fib(n) {
  if (n <= 1) return n;
  return fib(n - 2) + fib(n - 1);
}

for (var i = 0; i < 10; i = i) {
  print fib(i);
  i = i + 1;
}
```

Example of using the ternary operator:

```
print true and false ? "should not be truthy" : "should be falsy";

print true ? false ? "should not be nested truthy" : "should be nested falsy" : "should not be outer falsy";
```

Example of using the list data type:

```
// Use the '[' and ']' literals to define a new list
var x = [100];
print x;

// The extended grammar allows for nested lists and multiple indexing
var x = [[2], [1]];
print x[0][0];

// Just like any other data type, lists can be returned from functions
fun printHello() {
    return [10, 20];
}

// The precendece rules allow for indexing into a list and calling the returned object
print [printHello][0]();

// The precendece rules also allow to index into the return value of a called object
print printHello()[0];
```

Example of using appending and deleting from a list:

```
var x = [10];
x.append(20);
print x; // [10, 20]

// Delete an element from a list by providing the index of the element to delete
var x = [10];
x.delete(0);
print x; // []
```
