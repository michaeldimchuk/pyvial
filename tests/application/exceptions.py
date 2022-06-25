class CustomForbiddenError(Exception):
    pass


class CustomUnauthorizedError(Exception):
    pass


class ResourceCustomizedError(CustomUnauthorizedError):
    pass
