""" ========================= Scanner Error Messages ========================= """

UNTERMINATED_STRING = "Unterminated string."
INVALID_CHAR = "Unexpected character."

""" ========================= Parser Error Messages ========================= """

MISSING_SEMICOLON = "Expect ';' after expression."
INVALID_ASSIGNMENT = "Invalid assignment target."
MISSING_CLOSING_BRACE = "Expect '}' after block."
MISSING_IF_OPEN_BRACKET = "Expect '(' after 'if'."
MISSING_IF_CLOSE_BRACKET = "Expect ')' after if condition."
MISSING_WHILE_OPEN_BRACKET = "Expect '(' after 'while'."
MISSING_WHILE_CLOSE_BRACKET = "Expect ')' after while condition."
MISSING_FOR_OPEN_BRACE = "Expect '(' after 'for'."
MISSING_FOR_CLOSE_BRACE = "Expect ')' after for clauses."
MISSING_SEMICOLON_IN_FOR_LOOP_CONDITION = "Expect ';' after loop condition."

""" ========================= Interpreter Error Messages ========================= """

DIVIDE_BY_ZERO_ERROR = "Can not divide by zero."
EXPECT_TYPE_NUMBER = "Operands must be numbers."
EXPECT_TYPE_NUMBER_OR_STRING = "Operands must be two numbers or two strings."
INVALID_BINARY_EXPRESSION = "Operator is not a valid binary expression."
