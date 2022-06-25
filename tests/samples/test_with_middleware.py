from __future__ import annotations

from http import HTTPStatus

from vial import request
from vial.app import Vial
from vial.gateway import Gateway
from vial.middleware import CallChain
from vial.types import Request, Response

app = Vial(__name__)


@app.middleware
def log_events(event: Request, chain: CallChain) -> Response:
    app.logger.info("Began execution of %s", event.context)
    event.headers["custom-injected-header"] = "hello there"
    try:
        return chain(event)
    finally:
        app.logger.info("Completed execution of %s", event.context)


@app.get("/hello-world")
def hello_world() -> dict[str, str | list[str]]:
    return {"hello": "world", **request.get().headers}


def test_hello_world() -> None:
    response = Gateway(app).get("/hello-world")
    assert response.status == HTTPStatus.OK
    assert response.body == {"hello": "world", "custom-injected-header": ["hello there"]}
