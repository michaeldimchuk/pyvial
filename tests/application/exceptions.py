from http import HTTPStatus

from vial.exceptions import HTTPError


class CustomForbiddenError(Exception):
    pass


class CustomUnauthorizedError(Exception):
    pass


class ResourceCustomizedError(CustomUnauthorizedError):
    pass


class GatewayTimeoutError(HTTPError):
    status = HTTPStatus.GATEWAY_TIMEOUT
