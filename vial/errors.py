from http import HTTPStatus


class ServerError(Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR


class NotFoundError(ServerError):
    status = HTTPStatus.NOT_FOUND


class MethodNotAllowedError(ServerError):
    status = HTTPStatus.METHOD_NOT_ALLOWED
