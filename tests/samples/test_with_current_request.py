from http import HTTPStatus

from vial import request
from vial.app import Vial
from vial.gateway import Gateway

app = Vial(__name__)


@app.get("/hello-world")
def hello_world() -> dict[str, list[str]]:
    if not (query_params := request.get().query_parameters):
        raise ValueError("Must provide at least one query parameter")
    return dict(query_params)


def test_hello_world() -> None:
    response = Gateway(app).get("/hello-world?hello=world&goodbye=world1&goodbye=world2")
    assert response.status == HTTPStatus.OK
    assert response.body == {"hello": ["world"], "goodbye": ["world1", "world2"]}
