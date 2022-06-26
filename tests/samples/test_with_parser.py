from dataclasses import dataclass
from http import HTTPStatus
from uuid import UUID, uuid4

from vial.app import Vial
from vial.gateway import Gateway

app = Vial(__name__)


@dataclass
class User:
    user_id: UUID


@app.get("/users/{user_id:uuid}")
def get_user(user_id: UUID) -> User:
    if not isinstance(user_id, UUID):
        raise AssertionError("Invalid input")
    return User(user_id)


def test_get_user() -> None:
    user_id = str(uuid4())
    response = Gateway(app).get(f"/users/{user_id}")
    assert response.status == HTTPStatus.OK
    assert response.body == {"user_id": user_id}


def test_get_user_parser_failure() -> None:
    response = Gateway(app).get("/users/kenobi")
    assert response.status == HTTPStatus.BAD_REQUEST
