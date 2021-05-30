from http import HTTPStatus


class ServerError(Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR


class NotFoundError(Exception):
    status = HTTPStatus.NOT_FOUND


class MethodNotAllowedError(Exception):
    status = HTTPStatus.METHOD_NOT_ALLOWED
