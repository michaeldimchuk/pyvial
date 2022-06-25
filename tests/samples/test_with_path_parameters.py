from dataclasses import dataclass
from http import HTTPStatus

from vial.app import Vial
from vial.gateway import Gateway

app = Vial(__name__)


@dataclass
class User:
    user_id: str


@app.get("/users/{user_id}")
def get_user(user_id: str) -> User:
    return User(user_id)


def test_get_user() -> None:
    response = Gateway(app).get("/users/kenobi")
    assert response.status == HTTPStatus.OK
    assert response.body == {"user_id": "kenobi"}
