from http import HTTPStatus

from vial.app import Vial
from vial.gateway import Gateway

app = Vial(__name__)


@app.get("/hello-world")
def hello_world() -> dict[str, str]:
    return {"hello": "world"}


def test_hello_world() -> None:
    response = Gateway(app).get("/hello-world")
    assert response.status == HTTPStatus.OK
    assert response.body == {"hello": "world"}
