from http import HTTPStatus

import pytest

from vial import request
from vial.app import Vial
from vial.errors import BadRequestError, ErrorCode
from vial.gateway import Gateway

app = Vial(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}


@app.post("/stores/{store_id}")
def create_store(store_id: str) -> dict[str, str]:
    if not (body := request.get().body):
        raise BadRequestError(ErrorCode("INVALID_STORE_CONFIGURATION", "Should've added validation"))
    return {"store_id": store_id, **app.json.loads(body)}


@pytest.fixture(name="gateway")
def gateway_fixture() -> Gateway:
    return Gateway(app)


def test_health(gateway: Gateway) -> None:
    response = gateway.get("/health")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}


def test_create_store(gateway: Gateway) -> None:
    body = app.json.dumps({"store_name": "My cool store"})
    response = gateway.post("/stores/my-cool-store", body)
    assert response.status == HTTPStatus.OK
    assert response.body == {"store_id": "my-cool-store", "store_name": "My cool store"}


def test_create_store_no_body(gateway: Gateway) -> None:
    response = gateway.post("/stores/my-cool-store")
    assert response.status == HTTPStatus.BAD_REQUEST
    assert isinstance(response.body, dict)
    assert response.body[ErrorCode.CODE] == "INVALID_STORE_CONFIGURATION"
