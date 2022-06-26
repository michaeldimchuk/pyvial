from __future__ import annotations

import dataclasses
from collections import defaultdict
from http import HTTPStatus
from typing import Callable, Type, TypeVar, cast

from vial.exceptions import ServerError, VialError
from vial.types import Response

E = TypeVar("E", bound=Exception)


class ErrorHandler:

    DEFAULT_STATUSES = {
        Exception: HTTPStatus.INTERNAL_SERVER_ERROR,
        ValueError: HTTPStatus.BAD_REQUEST,
        NotImplementedError: HTTPStatus.NOT_IMPLEMENTED,
    }

    def __init__(self, name: str) -> None:
        self.name = name
        self.error_handlers: dict[str, dict[Type[Exception], Callable[[Exception], Response]]] = defaultdict(dict)
        self.register_handler(Exception, self._default_handler)
        self.register_handler(ServerError, self._server_error_handler)

    def register_handler(self, error_type: Type[Exception], handler: Callable[[E], Response]) -> None:
        self.error_handlers[self.name][error_type] = cast(Callable[[Exception], Response], handler)

    def __call__(self, resource: str, error: Exception) -> Response:
        for error_type in type(error).__mro__:
            if issubclass(error_type, Exception):
                if handler := self._get_error_handler(resource, error_type):
                    return handler(error)
        return self._default_handler(error)

    def _get_error_handler(self, resource: str, error_type: Type[Exception]) -> Callable[[Exception], Response] | None:
        """
        Tries to get the best matching error handler for the specified route. An error handler registered on a
        Resource rather than the global Vial application will always take precedence over the global erro handler.
        """
        return self.error_handlers[resource].get(error_type) or self.error_handlers[self.name].get(error_type)

    def _server_error_handler(self, error: ServerError) -> Response:
        return Response(dataclasses.asdict(error.error), status=error.status)

    def _default_handler(self, error: Exception) -> Response:
        response = dataclasses.asdict(VialError.UNKNOWN_ERROR.get(str(error)))
        return Response(response, status=self._get_native_status_code(error))

    def _get_native_status_code(self, error: Exception) -> HTTPStatus:
        for error_type in type(error).__mro__:
            if issubclass(error_type, Exception):
                if status := self.DEFAULT_STATUSES.get(error_type):
                    return status
        return HTTPStatus.INTERNAL_SERVER_ERROR


class ErrorHandlingAPI:
    error_handler_class: Type[ErrorHandler] = ErrorHandler

    def __init__(self, name: str) -> None:
        self.name = name
        self.default_error_handler = self.error_handler_class(name)

    def error_handler(
        self, *error_types: Type[Exception]
    ) -> Callable[[Callable[[E], Response]], Callable[[E], Response]]:
        """Binds the decorated function as the error handler for all provided exception types."""

        def error_handling_wrapper(function: Callable[[E], Response]) -> Callable[[E], Response]:
            for error_type in error_types:
                self.register_error_handler(error_type, function)
            return function

        return error_handling_wrapper

    def register_error_handler(self, error_type: Type[Exception], handler: Callable[[E], Response]) -> None:
        self.default_error_handler.register_handler(error_type, handler)

    def register_error_handlers(self, other: ErrorHandlingAPI) -> None:
        self.default_error_handler.error_handlers[other.name] = other.default_error_handler.error_handlers[other.name]
