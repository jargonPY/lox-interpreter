from data_types.lexical_token import Token


class ParseError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message  # ? Is it necessary if its already stored in the "super" class?


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message

    # todo implement equality operator
    # def __eq__(self, other: object) -> bool:
    #     return super().__eq__(__o)


class ReturnException(Exception):
    def __init__(self, value: object) -> None:
        super().__init__()
        self.value = value
