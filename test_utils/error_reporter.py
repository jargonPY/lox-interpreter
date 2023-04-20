from data_types.errors import LoxRuntimeError


class TestErrorReporter:
    def set_error(self, line: int, message: str) -> None:
        self.message = message

    def set_runtime_error(self, error: LoxRuntimeError) -> None:
        self.error = error
        self.message = error.message
