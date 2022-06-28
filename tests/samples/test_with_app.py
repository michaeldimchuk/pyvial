from http import HTTPStatus

from vial.app import Vial
from vial.gateway import Gateway

app = Vial(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}


def test_hello_world() -> None:
    response = Gateway(app).get("/health")
    assert response.status == HTTPStatus.OK
    assert response.body == {"status": "OK"}
