class ResourceNotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message


class BusinessRuleError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
