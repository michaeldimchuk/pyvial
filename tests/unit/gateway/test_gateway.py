from __future__ import annotations

from http import HTTPStatus
from typing import Callable

import pytest

from vial.gateway import Gateway
from vial.types import HTTPMethod, Response

from tests.application.application import app


@pytest.fixture(name="gateway")
def gateway_fixture() -> Gateway:
    return Gateway(app)


@pytest.mark.parametrize(
    "invoker, method",
    [(Gateway.post, HTTPMethod.POST), (Gateway.put, HTTPMethod.PUT), (Gateway.patch, HTTPMethod.PATCH)],
)
def test_methods_with_body(
    invoker: Callable[[Gateway, str, str | None, dict[str, str | list[str]] | None], Response],
    method: HTTPMethod,
    gateway: Gateway,
) -> None:
    response = invoker(gateway, "/method-test", None, {"hello": "world"})
    assert response.status == HTTPStatus.OK
    assert response.body == {"method": method.name}


@pytest.mark.parametrize("invoker, method", [(Gateway.get, HTTPMethod.GET), (Gateway.delete, HTTPMethod.DELETE)])
def test_methods_without_body(
    invoker: Callable[[Gateway, str, dict[str, str | list[str]] | None], Response],
    method: HTTPMethod,
    gateway: Gateway,
) -> None:
    response = invoker(gateway, "/method-test", {"hello": "world"})
    assert response.status == HTTPStatus.OK
    assert response.body == {"method": method.name}


def test_get_with_headers(gateway: Gateway) -> None:
    response = gateway.get("/return/headers/in/response", {"hello": "world", "goodbye": ["world"]})
    assert response.status == HTTPStatus.OK
    assert response.body == {"hello": ["world"], "goodbye": ["world"]}
