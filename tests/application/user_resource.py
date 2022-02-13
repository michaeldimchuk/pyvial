import dataclasses
from dataclasses import dataclass
from typing import Optional, Type

from vial.errors import NotFoundError
from vial.middleware import CallChain
from vial.resources import Resource
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
    scenario: Optional[tuple[Type[Exception], str]] = _ERROR_SCENARIOS.get(user_id)
    if scenario:
        raise scenario[0](scenario[1])
    return dataclasses.asdict(User(user_id, "John", "Doe"))
