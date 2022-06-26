from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from http import HTTPStatus

from vial.app import Resource
from vial.errors import ErrorCode, NotFoundError
from vial.middleware import CallChain
from vial.types import Request, Response

from tests.application.exceptions import ResourceCustomizedError

app = Resource(__name__)


@dataclass
class User:
    user_id: str
    first_name: str
    last_name: str


_ERROR_SCENARIOS = {"not_found": (NotFoundError, ErrorCode("USER_NOT_FOUND", "User not found"))}


@app.error_handler(ResourceCustomizedError)
def custom_error_handler(error: ResourceCustomizedError) -> Response:
    return Response({"message": str(error)}, status=HTTPStatus.IM_A_TEAPOT)


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


@app.get("/resource-custom-error-in-resource")
def resource_custom_error() -> None:
    raise ResourceCustomizedError("Raised from the resource")
