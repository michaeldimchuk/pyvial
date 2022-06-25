from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from vial.app import Resource
from vial.errors import NotFoundError
from vial.middleware import CallChain
from vial.types import Request, Response

app = Resource(__name__)


@dataclass
class User:
    user_id: str
    first_name: str
    last_name: str


_ERROR_SCENARIOS = {"not_found": (NotFoundError, "User not found")}


@app.middleware
def scoped_middleware(event: Request, chain: CallChain) -> Response:
    response = chain(event)
    response.headers["scoped"] = "scoped-middleware-executed"
    return response


@app.get("/users/{user_id}")
def get_user(user_id: str) -> dict[str, str]:
    if scenario := _ERROR_SCENARIOS.get(user_id):
        raise scenario[0](scenario[1])
    return dataclasses.asdict(User(user_id, "John", "Doe"))
