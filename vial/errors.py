from http import HTTPStatus


class ServerError(Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR


class BadRequestError(ServerError):
    status = HTTPStatus.BAD_REQUEST


class UnauthorizedError(ServerError):
    status = HTTPStatus.UNAUTHORIZED


class ForbiddenError(ServerError):
    status = HTTPStatus.FORBIDDEN


class NotFoundError(ServerError):
    status = HTTPStatus.NOT_FOUND


class MethodNotAllowedError(ServerError):
    status = HTTPStatus.METHOD_NOT_ALLOWED
