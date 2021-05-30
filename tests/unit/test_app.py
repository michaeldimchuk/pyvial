import json
from http import HTTPStatus
from typing import Any, Dict, Mapping, Set
from uuid import UUID

from vial.app import Vial
from vial.types import LambdaContext

from tests import loggers, resources

log = loggers.new(__name__)

app = Vial()


@app.parser("set")
def set_parser(value: str) -> Set[str]:
    return {value}


@app.get("/something/{some_value:uuid}/cool-stuff")
def my_route(some_value: UUID) -> Mapping[str, str]:
    log.info("In my_route, value of type %s is %s", type(some_value), some_value)
    return {"hello": "world"}


def test_hello_world(context: LambdaContext) -> None:
    event: Dict[str, Any] = resources.read("get-with-variables.json")
    response = app(event, context)
    assert response["statusCode"] == HTTPStatus.OK
    assert response["headers"] == {}
    assert json.loads(response["body"]) == {"hello": "world"}
