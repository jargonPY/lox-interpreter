from data_types.lexical_token import Token


class TestEnvironment:
    def define(self, variable_name: str, value: object) -> None:
        print(variable_name)

    def get(self, variable_name: Token):
        print(variable_name.lexeme)
