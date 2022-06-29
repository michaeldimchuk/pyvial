from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from http import HTTPStatus
from typing import Any


@dataclass
class ErrorCode:
    CODE = "code"
    MESSAGE = "message"

    code: str
    message: str


class ErrorCodeBuilder:
    value: tuple[int, str]
    name: str

    def get(self, *args: Any, **kwargs: Any) -> ErrorCode:
        return ErrorCode(self.name, self.value[1].format(*args, **kwargs))


class VialError(ErrorCodeBuilder, Enum):
    ROUTE_NOT_FOUND = auto(), "No route defined for resource {}"
    METHOD_NOT_ALLOWED = auto(), "No route defined for resource {} and method {}"
    PARSER_NOT_REGISTERED = auto(), "Parser '{}' is not registered"
    PARSER_ALREADY_EXISTS = auto(), "Parser '{}' is already registered"
    NOT_IN_REQUEST = auto(), "Not currently within a request"
    INVALID_TIMESTAMP_ZONE = auto(), "Only UTC timestamps are supported, got {}"
    UNKNOWN_ERROR = auto(), "{}"


class HTTPError(Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR


class ServerError(HTTPError):
    def __init__(self, error: ErrorCode) -> None:
        super().__init__(error.message)
        self.error = error


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
