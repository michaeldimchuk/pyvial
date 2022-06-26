from dataclasses import dataclass
from http import HTTPStatus
from uuid import uuid4

from vial.app import Vial
from vial.gateway import Gateway

app = Vial(__name__)


@dataclass
class User:
    user_id: str


@app.parser("list")
def list_parser(value: str) -> list[str]:
    return [value]


@app.get("/users/{user_ids:list}")
def get_users(user_ids: list[str]) -> list[User]:
    if not isinstance(user_ids, list) or len(user_ids) != 1:
        raise AssertionError("Invalid input")
    return list(map(User, user_ids))


def test_get_user() -> None:
    user_id = str(uuid4())
    response = Gateway(app).get(f"/users/{user_id}")
    assert response.status == HTTPStatus.OK
    assert response.body == [{"user_id": user_id}]
