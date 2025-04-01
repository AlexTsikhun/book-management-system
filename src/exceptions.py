class BaseDetailException(Exception):
    default_detail = "Something went wrong."

    def __init__(self, detail: str | None = None):
        if detail is None:
            detail = self.default_detail

        self.detail = detail


class DoesNotExistError(BaseDetailException):
    default_detail = "Not found."
