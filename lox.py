import sys
from data_types.stmt import Stmt
from data_types.errors import LoxRuntimeError
from interpreter.environment import Environment
from scanner.scanner import Scanner
from parser.parser import Parser
from resolver.resolver import Resolver
from interpreter.interpreter import Interpreter

"""
The primary reason we’re sticking this error reporting function in the main Lox class is because of that hadError field.

The other reason I pulled the error reporting out here instead of stuffing it into the scanner and other phases where
the error might occur is to remind you that it’s good engineering practice to separate the code that generates the
errors from the code that reports them.

Various phases of the front end will detect errors, but it’s not really their job to know how to present that to a user.
In a full-featured language implementation, you will likely have multiple ways errors get displayed: on stderr, in an
IDE’s error window, logged to a file, etc. You don’t want that code smeared all over your scanner and parser.

Ideally, we would have an actual abstraction, some kind of “ErrorReporter” interface that gets passed to the scanner and
parser so that we can swap out different reporting strategies. For our simple interpreter here, I didn’t do that, but I
did at least move the code for error reporting into a different class.
"""


class Lox:
    # Used to ensure we don’t try to execute code that has a known error.
    # Also, it lets us exit with a non-zero exit code like a good command line citizen should.
    had_error = False
    # If the user is running a Lox script from a file and a runtime error occurs,
    # we set an exit code when the process quits to let the calling process know.
    had_runtime_error = False

    def __init__(self) -> None:
        self.scanner = Scanner(self)
        self.parser = Parser(self)
        self.resolver = Resolver(self)
        self.interpreter = Interpreter(Environment(), self)

    def report(self, line: int, where: str, message: str):
        """
        Tells the user some syntax error occured.
        """
        print(f"[line {line}] Error {where}: {message}")
        # ? Why is the 'report' method setting this flag rather than the 'error' method?
        self.had_error = True

    def set_error(self, line: int, message: str):
        """
        Reports an error message.
        """
        self.report(line, "", message)

    def set_runtime_error(self, error: LoxRuntimeError):
        print("LoxRuntimeError: ", error.message)
        self.had_runtime_error = True

    def run(self, source: str) -> list[Stmt]:
        tokens = self.scanner.scan(source)

        statements = self.parser.parse(tokens)

        # Stop if there are parsing errors.
        if self.had_error:
            return []

        resolved_local_vars = self.resolver.resolve(statements)

        # Stop if there are resolution errors.
        if self.had_error:
            return []

        self.interpreter.interpret(statements, resolved_local_vars)

        return statements

    def runFile(self, file_path: str):
        with open(file_path, "r") as f:
            file_contents = f.read()
            self.run(file_contents)

        if self.had_error:
            sys.exit(65)

        if self.had_runtime_error:
            sys.exit(70)

    def runPrompt(self):
        while True:
            line = input("> ")
            self.run(line)
            self.had_error = False


def main() -> None:
    lox = Lox()
    if len(sys.argv) > 2:
        print("Usage: pyLox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        lox.runFile(sys.argv[1])
    else:
        lox.runPrompt()


if __name__ == "__main__":
    main()
