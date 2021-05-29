from typing import Any, Dict
from uuid import UUID

from vial.app import Vial
from vial.types import LambdaContext

from tests import loggers, resources

app = Vial()

log = loggers.new(__name__)


@app.get("/something/{some_value:uuid}/cool-stuff")
def my_route(some_value: UUID) -> str:
    log.info("In my_route, value of type %s is %s", type(some_value), some_value)
    return f"Hello there {some_value}"


def test_hello_world(context: LambdaContext) -> None:
    event: Dict[str, Any] = resources.read("get-with-variables.json")
    app(event, context)
