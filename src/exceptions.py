class BaseDetailException(Exception):
    default_detail = "Something went wrong."

    def __init__(self, detail: str | None = None):
        if detail is None:
            detail = self.default_detail

        self.detail = detail


class DoesNotExistError(BaseDetailException):
    default_detail = "Not found."


class ValidationError(Exception):
    """Input data validation failed."""

    def __init__(self, field: str, messages: list[str]) -> None:
        self.field = field
        self.messages = messages
