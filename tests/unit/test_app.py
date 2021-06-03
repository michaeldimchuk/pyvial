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


def test_get_user_not_found(gateway: Gateway) -> None:
    response = gateway.get("/users/not_found")
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body == {"message": "User not found"}
