from http import HTTPStatus
from typing import Any
from unittest.mock import patch

import pytest

from vial.gateway import Gateway
from vial.types import HTTPMethod

from tests.application.application import app, app_without_middleware


@pytest.fixture(scope="module", name="gateway")
def gateway_fixture() -> Gateway:
    return Gateway(app)


def test_no_middleware() -> None:
    response = Gateway(app_without_middleware).get("/health")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}
    assert "logged" not in response.headers


def test_health(gateway: Gateway) -> None:
    response = gateway.get("/health")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}
    assert response.headers["logged"] == "middleware-executed"
    assert "scoped" not in response.headers


def test_response_returned(gateway: Gateway) -> None:
    response = gateway.get("/response-returned")
    assert response.status == HTTPStatus.ACCEPTED
    assert response.body == {"status": "OK"}
    assert response.headers["custom-header"] == "custom-value"


def test_tuple_returned(gateway: Gateway) -> None:
    response = gateway.get("/tuple-returned")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}
    assert response.headers["custom-header"] == "custom-value"


def test_string_returned(gateway: Gateway) -> None:
    response = gateway.get("/string-returned")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}


def test_parser(gateway: Gateway) -> None:
    response = gateway.get("/parser-type-returned/hello_world")
    assert response.status == HTTPStatus.OK
    assert response.body == {"type": str(list), "value": list("hello_world")}


def test_get_user_scoped_middleware(gateway: Gateway) -> None:
    response = gateway.get("/users/12345")
    assert response.status == HTTPStatus.OK
    assert response.headers["logged"] == "middleware-executed"
    assert response.headers["scoped"] == "scoped-middleware-executed"
    assert response.body == {"user_id": "12345", "first_name": "John", "last_name": "Doe"}


def test_get_user_not_found(gateway: Gateway) -> None:
    response = gateway.get("/users/not_found")
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body == {"message": "User not found"}


def test_query_params(gateway: Gateway) -> None:
    response = gateway.get("/query-params-test?hello=world&hello=monday&goodbye=world")
    assert response.status == HTTPStatus.OK
    assert response.body == {"hello": ["world", "monday"], "goodbye": ["world"]}


def test_custom_forbidden_error(gateway: Gateway) -> None:
    response = gateway.get("/custom-forbiden-error")
    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body == {"message": "Very secret"}


def test_custom_unauthorized_error(gateway: Gateway) -> None:
    response = gateway.get("/custom-unauthorized-error")
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.body == {"message": "Learn to type passwords"}


def test_not_found_error(gateway: Gateway) -> None:
    request = _build_gateway_event(HTTPMethod.GET, "/this-probably-isnt-defined")
    response = gateway.build_response(gateway.app(request, gateway.get_context()))
    assert response.status == HTTPStatus.NOT_FOUND


def test_method_not_allowed(gateway: Gateway) -> None:
    request = _build_gateway_event(HTTPMethod.PATCH, "/health")
    response = gateway.build_response(gateway.app(request, gateway.get_context()))
    assert response.status == HTTPStatus.METHOD_NOT_ALLOWED


def _build_gateway_event(method: HTTPMethod, path: str) -> dict[str, Any]:
    return {
        "httpMethod": method.name,
        "resource": path,
        "path": path,
        "multiValueHeaders": {},
        "multiValueQueryStringParameters": {},
        "pathParameters": {},
        "body": None,
    }


@patch.dict(app.default_error_handler.error_handlers, {Exception: None})
def test_missing_default_handler(gateway: Gateway) -> None:
    response = gateway.get("/really-bad-error")
    assert response.status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.body == {"message": "This can't happen"}


@patch.dict(app.default_error_handler.error_handlers, {Exception: None})
@patch.dict(app.default_error_handler.DEFAULT_STATUSES, {Exception: None})
def test_missing_default_handler_and_default_status(gateway: Gateway) -> None:
    response = gateway.get("/really-bad-error")
    assert response.status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.body == {"message": "This can't happen"}


@pytest.mark.parametrize("method", HTTPMethod)
def test_method_bindings(method: HTTPMethod, gateway: Gateway) -> None:
    response = gateway.request(method, "/method-test")
    assert response.status == HTTPStatus.OK
    assert response.body == {"method": method.name}
