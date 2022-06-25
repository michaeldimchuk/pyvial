from dataclasses import dataclass
from http import HTTPStatus

from vial.app import Resource, Vial
from vial.gateway import Gateway

stores_app = Resource(__name__)


@dataclass
class Store:
    store_id: str


@stores_app.get("/stores/{store_id}")
def get_store(store_id: str) -> Store:
    return Store(store_id)


app = Vial(__name__)

app.register_resource(stores_app)


def test_get_store() -> None:
    response = Gateway(app).get("/stores/my-cool-store")
    assert response.status == HTTPStatus.OK
    assert response.body == {"store_id": "my-cool-store"}
