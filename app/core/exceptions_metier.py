

class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: int = 400,
        errors: dict | None = None,
    ):
        self.message = message
        self.code = code
        self.errors = errors or {}
        super().__init__(message)

class RaiseException(AppException):
    pass

