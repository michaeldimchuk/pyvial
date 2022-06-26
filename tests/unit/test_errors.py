from http import HTTPStatus
from typing import Type

import pytest

from vial.exceptions import (
    BadRequestError,
    ForbiddenError,
    MethodNotAllowedError,
    NotFoundError,
    ServerError,
    UnauthorizedError,
)


@pytest.mark.parametrize(
    "error, status",
    [
        (BadRequestError, HTTPStatus.BAD_REQUEST),
        (ForbiddenError, HTTPStatus.FORBIDDEN),
        (MethodNotAllowedError, HTTPStatus.METHOD_NOT_ALLOWED),
        (NotFoundError, HTTPStatus.NOT_FOUND),
        (ServerError, HTTPStatus.INTERNAL_SERVER_ERROR),
        (UnauthorizedError, HTTPStatus.UNAUTHORIZED),
    ],
)
def test_status(error: Type[ServerError], status: HTTPStatus) -> None:
    assert error.status == status
