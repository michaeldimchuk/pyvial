import dataclasses
from dataclasses import dataclass
from typing import Mapping, Optional, Tuple, Type

from vial.errors import NotFoundError
from vial.resources import Resource

app = Resource()


@dataclass
class User:
    user_id: str
    first_name: str
    last_name: str


_ERROR_SCENARIOS = {"not_found": (NotFoundError, "User not found")}


@app.get("/users/{user_id}")
def get_user(user_id: str) -> Mapping[str, str]:
    scenario: Optional[Tuple[Type[Exception], str]] = _ERROR_SCENARIOS.get(user_id)
    if scenario:
        raise scenario[0](scenario[1])
    return dataclasses.asdict(User(user_id, "John", "Doe"))
