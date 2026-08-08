class ResourceNotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message


class BusinessRuleError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ForbiddenError(Exception):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message)
        self.message = message
