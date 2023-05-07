from typing import Protocol
from data_types.lexical_token import Token
from data_types.token_type import TokenType
from data_types.errors import ParseError
from data_types.expr import *
from data_types.stmt import *
from data_types.error_messages import *

"""
todo:

1. Many calls to 'self.next_token_matches()' are followed by 'self.consume_token()'. Add a helper that does both 'self.next_token_matches_and_consumes()'.
2. Add the grammar rule definition as part comments for each function.
"""


class ErrorReporter(Protocol):
    def set_error(self, line: int, message: str) -> None:
        ...


class Parser:
    """
    Maps a sequence of tokens to expressions.

    The class has two types of methods:

    1. Methods help to manage the token stream and to ensure that tokens are properly consumed and processed.
       isEOF, peek, consume_token, consume_token_if_matching, check_token_type, next_token_matches, and synchronize.

    2. Methods that are used by the parse method to construct Expr objects based on the grammar of the input language.
        expression, term, factor, and primary
    """

    def __init__(self, error_reporter: ErrorReporter) -> None:
        self.error_reporter = error_reporter
        self.tokens: list[Token] = []
        self.pos: int = 0  # Points to the next token to be consumed
        self.statements: list[Stmt] = []

    def isEOF(self) -> bool:
        return self.tokens[self.pos].type == TokenType.EOF

    def peek(self) -> Token:
        """
        This method performs a one token 'lookahead' and does not consume the token.
        It looks at the current unconsumed token.

        Assumptions:
        Does not check isEOF. Assumes that 'self.pos' is not out of bounds.
        """
        return self.tokens[self.pos]

    def check_token_type(self, token_type: TokenType) -> bool:
        """
        Returns true if the current token is of the given type.
        Used as a helper method for 'next_token_matches'.
        """
        if self.isEOF():
            return False
        return self.peek().type == token_type

    def next_token_matches(self, token_types: list[TokenType]) -> bool:
        """
        Checks to see if the current token has any of the given types. If so,
        it returns True, otherwise it returns False.
        """
        for token_type in token_types:
            if self.check_token_type(token_type):
                return True

        return False

    def consume_token(self) -> Token:
        """
        Consumes the next token in the token stream and returns it.

        Assumptions:
        Does not check isEOF. Assumes that 'self.pos' is not out of bounds.
        """
        curr_token = self.tokens[self.pos]
        self.pos += 1
        return curr_token

    def consume_token_if_matching(self, token_type: TokenType, message: str) -> Token:
        """
        Consumes a token only if it matches the expected 'token_type', otherwise it throws a ParseError.

        Cetain expressions expect a certain order of tokens to be fully parsed (ex. STRING / NUMBER to create a Literal, semicolon to end an Expr etc.).
        """

        if self.next_token_matches([token_type]):
            return self.consume_token()
        raise ParseError(self.peek(), message)

    def synchronize(self) -> None:
        """
        Discard tokens until an expression boundary is found (i.e. a semicolon).

        This method is called after a ParseException occurs in order to return the parser
        to a valid state so that it can report several errors in one run, rather than exiting
        after every single error.
        """

        while not self.isEOF():
            self.consume_token()

            if self.next_token_matches([TokenType.SEMICOLON]):
                self.consume_token()
                return

    def _reset_parser(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.statements = []

    def parse(self, tokens: list[Token]) -> list[Stmt]:
        """
        Throws an "IndexError: list index out of range" exception if the tokens list is empty.
        Throws an "IndexError" if "EOF" token is missing.
        """
        self._reset_parser(tokens)

        while not self.isEOF():
            try:
                statement = self.declaration()
                self.statements.append(statement)
            except ParseError as e:
                self.synchronize()
                self.error_reporter.set_error(1, e.message)

        return self.statements

    def declaration(self) -> Stmt:
        """
        declaration ->  varDecl | funDecl | statement ;

        This method is the method we call repeatedly when parsing a series of statements
        in a block or a script, so it’s the right place to synchronize when the parser
        goes into panic mode.

        This gets it back to trying to parse the beginning of the next statement or declaration.
        """
        if self.next_token_matches([TokenType.VAR]):
            self.consume_token()  # Consumes the 'var' token
            return self.varDeclaration()

        if self.next_token_matches([TokenType.FUN]):
            self.consume_token()  # Consumes the 'fun' token
            return self.function()

        if self.next_token_matches([TokenType.CLASS]):
            self.consume_token()  # Consumes the 'class' token
            return self.classDeclaration()

        return self.statement()

    def varDeclaration(self) -> Stmt:
        variable_name = self.consume_token_if_matching(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.next_token_matches([TokenType.EQUAL]):
            self.consume_token()  # Consumes the '=' token
            initializer = self.expression()

        self.consume_token_if_matching(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(variable_name, initializer)

    def classDeclaration(self) -> Stmt:
        """
        classDecl -> "class" IDENTIFIER "{" function* "}" ;
        """

        class_name = self.consume_token_if_matching(TokenType.IDENTIFIER, "Expect class name.")
        self.consume_token_if_matching(TokenType.LEFT_BRACE, "Expect '{' after class name.")

        methods = []
        # Parse class methods
        while not self.next_token_matches([TokenType.RIGHT_BRACE]) and not self.isEOF():
            methods.append(self.function())

        self.consume_token_if_matching(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return ClassStmt(class_name, methods)

    def function(self) -> FunctionStmt:
        """
        funDecl -> "fun" function ;

        function -> IDENTIFIER "(" parameters? ")" block ;

        The function delclaration statement, 'funDecl', uses a seperate helper rule 'function', which is
        also used when declaring methods (hence seperating it into a helper method).

        parameters -> IDENTIFIER ( "," IDENTIFIER )* ;

        The 'parameters' rule is similar to the 'arguments' rule except that each parameter is an identifier,
        not an expression.
        """

        func_name = self.consume_token_if_matching(TokenType.IDENTIFIER, "Expect function name.")

        self.consume_token_if_matching(TokenType.LEFT_PAREN, "Expect '(' after function name.")

        parameters = []
        # Handle the zero parameters case by checking if the next token is ')'
        if not self.next_token_matches([TokenType.RIGHT_PAREN]):
            # Parse the first parameter
            parameter_token = self.consume_token_if_matching(TokenType.IDENTIFIER, "Expect parameter name.")
            parameters.append(parameter_token)
            # Parse the rest of the comma-seperated parameters
            while self.next_token_matches([TokenType.COMMA]):
                self.consume_token()  # Consume ','
                parameter_token = self.consume_token_if_matching(TokenType.IDENTIFIER, "Expect parameter name.")
                parameters.append(parameter_token)

        self.consume_token_if_matching(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        block = self.blockStatement()

        return FunctionStmt(func_name, parameters, block)

    def statement(self) -> Stmt:
        """
        statement -> exprStmt | ifStmt | whileStmt | forStmt | printStmt | blockStmt | returnStmt ;

        REMOVE THIS AFTER TAKING NOTES:

        Remember how statement() tries to parse an expression statement if no other statement matches?
        And expression() reports a syntax error if it can’t parse an expression at the
        current token? That chain of calls ensures we report an error if a valid declaration
        or statement isn’t parsed.
        """

        if self.next_token_matches([TokenType.WHILE]):
            return self.whileStatement()

        if self.next_token_matches([TokenType.FOR]):
            return self.forStatement()

        if self.next_token_matches([TokenType.IF]):
            return self.ifStatement()

        if self.next_token_matches([TokenType.PRINT]):
            return self.printStatement()

        if self.next_token_matches([TokenType.LEFT_BRACE]):
            """
            Having 'blockStatement()' return a list of statements and leaving it to 'statement()' to wrap the
            list in a 'Stmt.Block' looks a little odd. I did it that way because we’ll reuse block() later
            for parsing function bodies and we don’t want that body wrapped in a Stmt.Block.
            """
            statements = self.blockStatement()
            return BlockStmt(statements)

        if self.next_token_matches([TokenType.RETURN]):
            return self.returnStatement()

        return self.expressionStatement()

    def returnStatement(self) -> Stmt:
        """
        returnStmt -> "return" expression? ";" ;
        """

        return_keyword = self.consume_token()  # Consumes the 'return' token
        value = None

        if not self.next_token_matches([TokenType.SEMICOLON]):
            value = self.expression()

        self.consume_token_if_matching(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmt(return_keyword, value)

    def whileStatement(self) -> Stmt:
        """
        whileStmt -> "while" "(" expression ")" statement ;
        """
        self.consume_token()  # Consumes the 'while' token

        self.consume_token_if_matching(TokenType.LEFT_PAREN, MISSING_WHILE_OPEN_BRACKET)
        condition_expr = self.expression()
        self.consume_token_if_matching(TokenType.RIGHT_PAREN, MISSING_WHILE_CLOSE_BRACKET)
        body = self.statement()
        return WhileStmt(condition_expr, body)

    def forStatement(self) -> Stmt:
        """
        forStmt -> "for" "(" ( varDecl | exprStmt | ";" ) expression? ";" expression? ")" statement ;

        Example:
        for (var i = 0; i < 10; i = i + 1) print i;
        """
        self.consume_token()  # Consumes the 'for' token

        self.consume_token_if_matching(TokenType.LEFT_PAREN, MISSING_FOR_OPEN_BRACE)

        # Parse the initializer
        if self.next_token_matches([TokenType.SEMICOLON]):
            self.consume_token()
            initializer = None
        elif self.next_token_matches([TokenType.VAR]):
            self.consume_token()
            initializer = self.varDeclaration()
        else:
            # Wrap the expression wrap it in an expression statement so that the initializer is always of type 'Stmt'
            initializer = self.expressionStatement()

        # Parse the condition
        condition = None
        if self.peek().type != TokenType.SEMICOLON:
            condition = self.expression()
        self.consume_token_if_matching(TokenType.SEMICOLON, MISSING_SEMICOLON_IN_FOR_LOOP_CONDITION)

        # Parse the increment
        increment = None
        if self.peek().type != TokenType.RIGHT_PAREN:
            increment = self.expression()
        self.consume_token_if_matching(TokenType.RIGHT_PAREN, MISSING_FOR_CLOSE_BRACE)

        body = self.statement()

        """
        The increment, if there is one, executes after the body in each iteration of the loop.
        We do that by replacing the body with a little block that contains the original body
        followed by an expression statement that evaluates the increment.
        """
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])

        """
        If the condition is omitted, set the condition to 'true' to make an infinite loop.
        """
        if condition is None:
            condition = Literal(True)
        body = WhileStmt(condition, body)

        """
        If there is an initializer, it runs once before the entire loop.
        """
        if not initializer is None:
            body = BlockStmt([initializer, body])

        return body

    def ifStatement(self) -> Stmt:
        """
        ifStmt -> "if" "(" expression ")" statement ( "else" statement )? ;
        """
        self.consume_token()  # Consumes the 'if' token

        self.consume_token_if_matching(TokenType.LEFT_PAREN, MISSING_IF_OPEN_BRACKET)
        condition_expr = self.expression()
        self.consume_token_if_matching(TokenType.RIGHT_PAREN, MISSING_IF_CLOSE_BRACKET)

        then_branch = self.statement()
        else_branch = None
        if self.next_token_matches([TokenType.ELSE]):
            self.consume_token()  # Consumes the 'else' token
            else_branch = self.statement()

        return IfStmt(condition_expr, then_branch, else_branch)

    def printStatement(self) -> Stmt:
        self.consume_token()  # Consumes the 'PRINT' token

        value_to_print = self.expression()
        self.consume_token_if_matching(TokenType.SEMICOLON, MISSING_SEMICOLON)

        return PrintStmt(value_to_print)

    def blockStatement(self) -> list[Stmt]:
        self.consume_token()  # Consumes the '{' token

        statements = []
        while not self.next_token_matches([TokenType.RIGHT_BRACE]) and not self.isEOF():
            statements.append(self.declaration())

        self.consume_token_if_matching(TokenType.RIGHT_BRACE, MISSING_CLOSING_BRACE)
        return statements

    def expressionStatement(self) -> Stmt:
        value = self.expression()

        self.consume_token_if_matching(TokenType.SEMICOLON, MISSING_SEMICOLON)

        # * Final fallthrough case when parsing a statement, since it’s hard to proactively recognize an expression from its first token.
        return ExpressionStmt(value)

    # ? Is this method required or can it be replaced by 'expressionStatement'?
    def expression(self) -> Expr:
        """
        expression -> assignment;
        """
        expr = self.assignment()
        # self.consume_token_if_matching(TokenType.SEMICOLON, "Expected semicolon.")

        return expr

    def assignment(self) -> Expr:
        """
        Note assignment is considered an expression.

        assignment -> IDENTIFIER "=" assignment | ternary;

        Updated assignment expression grammar:

        assignment -> (call ".")? IDENTIFIER ( "[" logic_or "]" )* "=" assignment | ternary;

        Extends the rule for assignment to allow dotted identifiers on the left-hand side.

        This would allow for: x[0] = 100;
        """
        expr = self.ternary()

        # todo implement assignment to list index: x[0] = 100;

        if self.next_token_matches([TokenType.EQUAL]):
            equals = self.consume_token()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(expr.variable_name, value)

            if isinstance(expr, Get):
                return Set(expr.property_name, expr.obj, value)

            # ? Why does this raise "ParseError" instead of calling "consume_token_if_matching" like other methods?
            # todo change to "consume_token_if_matching"
            raise ParseError(equals, INVALID_ASSIGNMENT)

        return expr

    def ternary(self) -> Expr:
        expr = self.logic_or()

        if self.next_token_matches([TokenType.QUESTION]):
            self.consume_token()  # Consumes the "?" token
            truthy = self.ternary()

            self.consume_token_if_matching(TokenType.COLON, "Expect ':' after ternary truthy expression.")

            falsy = self.ternary()
            return Ternary(expr, truthy, falsy)

        return expr

    def logic_or(self) -> Expr:
        """
        logic_or -> logic_and ( "or" logic_and )* ;
        """
        expr = self.logic_and()

        while self.next_token_matches([TokenType.OR]):
            operator = self.consume_token()
            right = self.logic_and()
            expr = Logical(expr, operator, right)

        return expr

    def logic_and(self) -> Expr:
        """
        logic_and -> equality ( "and" equality )* ;
        """
        expr = self.equality()

        while self.next_token_matches([TokenType.AND]):
            operator = self.consume_token()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.next_token_matches([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator = self.consume_token()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.next_token_matches(
            [TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL]
        ):
            operator = self.consume_token()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.next_token_matches([TokenType.MINUS, TokenType.PLUS]):
            operator = self.consume_token()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.next_token_matches([TokenType.SLASH, TokenType.STAR]):
            operator = self.consume_token()
            right = self.primary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.next_token_matches([TokenType.BANG, TokenType.MINUS]):
            operator = self.consume_token()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self) -> Expr:
        """
        call -> primary ( "(" arguments? ")" )* ;

        This rule matches a primary expression followed by zero or more function calls. If there are no
        parentheses, this parses a bare primary expression. Otherwise, each call is recognized by a pair
        of parentheses with an optional list of arguments inside.

        Similar to parsing infix operators. First parse the primary expression, the "left operand" to
        the call. Then each time there is a '(' call 'finish_call` using the previously parsed expression
        as the callee. Then loop to see if the result itself is called.

        Updated call expression grammar:

        call -> primary ( "(" arguments? ")" | "." IDENTIFIER )* ;

        The "Get" expression, an expression followed by . and an identifier reads the property with that name
        from the object the expression evaluates to. The "." has the same precedence has the parentheses in a
        call expression so they are put combined in the same grammar rule.
        """
        expr = self.grouping()

        # This while loop corresponds to the "*" (zero or more occurences) in the grammar rule.
        while True:
            if self.next_token_matches([TokenType.LEFT_PAREN]):
                self.consume_token()  # Consume '('
                expr = self.finish_call(expr)
            elif self.next_token_matches([TokenType.DOT]):
                self.consume_token()  # Consume '.'
                property_name = self.consume_token_if_matching(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(property_name, expr)
            else:
                break

        return expr

    # ? Why not rename this function to 'arguments' since it parses the arguments of a function call?
    def finish_call(self, callee: Expr) -> Expr:
        """
        arguments -> expression ( "," expression )* ;

        This rule requires at least one argument expression, followed by zero or more other expressions,
        each preceded by a comma. To handle zero-argument calls, the call rule itself considers the entire
        arguments production to be optional.
        """
        arguments: list[Expr] = []

        # Handle the zero aruments case by checking if the next token is ')'
        if not self.next_token_matches([TokenType.RIGHT_PAREN]):
            # Parse the first argument
            arguments.append(self.expression())
            # Parse the rest of the comma-seperated arguments
            while self.next_token_matches([TokenType.COMMA]):
                self.consume_token()  # Consume ','
                arguments.append(self.expression())

        closing_paren = self.consume_token_if_matching(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, closing_paren, arguments)

    def grouping(self) -> Expr:
        if self.next_token_matches([TokenType.LEFT_PAREN]):
            self.consume_token()  # Consume '('
            expr = self.expression()
            self.consume_token_if_matching(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        return self.lox_list_index()

    def lox_list_index(self) -> Expr:
        """
        lox_list_index -> lox_list ( "[" logic_or "]" )* ;

        This grammar rule allows for:
            list[0]();

        but not for:
            func()[0];
        """

        expr = self.lox_list()

        # While loop allows for multiple indexing (ex. var x = [[2], [1]];, print x[0][0];).
        while True:
            # todo change the definition of the grammar rule to acommedate both
            if self.next_token_matches([TokenType.LEFT_PAREN]):
                self.consume_token()
                expr = self.finish_call(expr)

            if self.next_token_matches([TokenType.LEFT_BRACKET]):
                self.consume_token()  # Consume '['
                index = self.logic_or()
                self.consume_token_if_matching(TokenType.RIGHT_BRACKET, "Expect ']' after list index.")
                expr = LoxListIndex(expr, index)
            else:
                break

        return expr

    def lox_list(self) -> Expr:
        """
        lox_list -> primary | "[" ( logic_or ( "," logic_or )*  )? "]" ;
        """
        if self.next_token_matches([TokenType.LEFT_BRACKET]):
            self.consume_token()  # Consume '['
            items: list[Expr] = []

            # Handle the zero aruments case by checking if the next token is ')'
            if not self.next_token_matches([TokenType.RIGHT_BRACKET]):
                # Parse the first item
                items.append(self.logic_or())
                # Parse the rest of the comma-seperated arguments
                while self.next_token_matches([TokenType.COMMA]):
                    self.consume_token()  # Consume ','
                    items.append(self.logic_or())

            self.consume_token_if_matching(TokenType.RIGHT_BRACKET, "Expect ']' after list expression.")
            return LoxList(items)

        return self.primary()

    # ? Catch all method expressions of the highest precedence or whose precedence is irrelevant.
    def primary(self) -> Expr:
        # Convert Lox literals to Python literals
        if self.next_token_matches([TokenType.TRUE]):
            self.consume_token()
            return Literal(True)
        if self.next_token_matches([TokenType.FALSE]):
            self.consume_token()
            return Literal(False)
        if self.next_token_matches([TokenType.NIL]):
            self.consume_token()
            return Literal(None)

        if self.next_token_matches([TokenType.IDENTIFIER]):
            return Variable(self.consume_token())

        if self.next_token_matches([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self.consume_token().literal)

        if self.next_token_matches([TokenType.THIS]):
            return This(self.consume_token())

        raise ParseError(self.consume_token(), "Expect expression.")
