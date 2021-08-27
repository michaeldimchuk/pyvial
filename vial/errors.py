from http import HTTPStatus
from typing import Callable, MutableMapping, Type, TypeVar, cast

from vial.types import Response

E = TypeVar("E", bound=Exception)


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


class ErrorHandler:

    DEFAULT_STATUSES = {
        Exception: HTTPStatus.INTERNAL_SERVER_ERROR,
        ValueError: HTTPStatus.BAD_REQUEST,
        NotImplementedError: HTTPStatus.NOT_IMPLEMENTED,
    }

    def __init__(self) -> None:
        self.error_handlers: MutableMapping[Type[Exception], Callable[[Exception], Response]] = {}
        self.register_handler(Exception, self._default_handler)

    def register_handler(self, error_type: Type[Exception], handler: Callable[[E], Response]) -> None:
        self.error_handlers[error_type] = cast(Callable[[Exception], Response], handler)

    def __call__(self, error: Exception) -> Response:
        for error_type in type(error).__mro__:
            if issubclass(error_type, Exception):
                handler = self.error_handlers.get(error_type)
                if handler:
                    return handler(error)
        return self._default_handler(error)

    def _default_handler(self, error: Exception) -> Response:
        return Response({"message": str(error)}, status=self._get_status_code(error))

    def _get_status_code(self, error: Exception) -> HTTPStatus:
        if isinstance(error, ServerError):
            return error.status
        return self._get_native_status_code(error)

    def _get_native_status_code(self, error: Exception) -> HTTPStatus:
        for error_type in type(error).__mro__:
            if issubclass(error_type, Exception):
                status = self.DEFAULT_STATUSES.get(error_type)
                if status:
                    return status
        return HTTPStatus.INTERNAL_SERVER_ERROR


class ErrorHandlingAPI:

    error_handler_class: Type[ErrorHandler] = ErrorHandler

    def __init__(self) -> None:
        self.default_error_handler = self.error_handler_class()

    def error_handler(
        self, *error_types: Type[Exception]
    ) -> Callable[[Callable[[E], Response]], Callable[[E], Response]]:
        def error_handling_wrapper(function: Callable[[E], Response]) -> Callable[[E], Response]:
            for error_type in error_types:
                self.register_error_handler(error_type, function)
            return function

        return error_handling_wrapper

    def register_error_handler(self, error_type: Type[Exception], handler: Callable[[E], Response]) -> None:
        self.default_error_handler.register_handler(error_type, handler)
