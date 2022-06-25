from decimal import Decimal
from http import HTTPStatus
from typing import Any

import simplejson

from vial.app import Vial
from vial.gateway import Gateway
from vial.json import Json


class SimpleJson(Json):
    @staticmethod
    def dumps(value: Any) -> str:
        return simplejson.dumps(value)

    @staticmethod
    def loads(value: str) -> Any:
        return simplejson.loads(value)


class SimpleJsonVial(Vial):
    json_class = SimpleJson


app = SimpleJsonVial(__name__)


@app.get("/prices")
def get_prices() -> dict[str, Decimal]:
    # Decimal is not supported natively by the json module, but is by simplejson.
    return {"bread": Decimal("42.24"), "cheese": Decimal("129.34")}


def test_get_prices() -> None:
    response = Gateway(app).get("/prices")
    assert response.status == HTTPStatus.OK
    assert response.body == {"bread": 42.24, "cheese": 129.34}
