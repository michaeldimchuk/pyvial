from http import HTTPStatus

import pytest

from vial.gateway import Gateway

from tests.application.application import app


@pytest.fixture(scope="module", name="gateway")
def gateway_fixture() -> Gateway:
    return Gateway(app)


def test_health(gateway: Gateway) -> None:
    response = gateway.get("/health")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}
    assert response.headers["logged"] == "middleware-executed"
    assert "scoped" not in response.headers


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
