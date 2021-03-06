from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from http import HTTPStatus
from typing import Any, Iterator, MutableMapping, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class MultiDict(MutableMapping[K, list[V]]):  # pylint: disable=too-many-ancestors
    def __init__(self, values: dict[K, list[V]] | None = None) -> None:
        super().__init__()
        self._values = values or {}

    def __delitem__(self, key: K) -> None:
        del self._values[key]

    def __getitem__(self, key: K) -> list[V]:
        return self._values[key]

    def get_first(self, key: K) -> V:
        return self._values[key][0]

    def extend(self, key: K, value: list[V]) -> None:
        if (existing_values := self._values.get(key)) is not None:
            existing_values.extend(value)
        else:
            self._values[key] = value

    def add(self, key: K, value: V) -> None:
        if (existing_values := self._values.get(key)) is not None:
            existing_values.append(value)
        else:
            self._values[key] = [value]

    def __iter__(self) -> Iterator[K]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __setitem__(self, key: K, value: list[V] | V) -> None:
        if isinstance(value, list):
            self._values[key] = value
        else:
            self._values[key] = [value]

    def __str__(self) -> str:
        return str(self._values)

    def __repr__(self) -> str:
        return repr(self._values)


@dataclass
class CognitoIdentity:
    cognito_identity_id: str
    cognito_identity_pool_id: str


@dataclass
class MobileClient:
    installation_id: str
    app_title: str
    app_version_name: str
    app_version_code: str
    app_package_name: str


@dataclass
class ClientContext:
    client: MobileClient
    custom: dict[str, Any]
    env: dict[str, Any]


@dataclass
class LambdaContext:
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: CognitoIdentity | None = None
    client_context: ClientContext | None = None

    @staticmethod
    def get_remaining_time_in_millis() -> int:
        """
        This is never used at runtime, the AWS provided context is used instead,
        and this is just a placeholder for tests and type hints.
        """
        return 30_000


class HTTPMethod(Enum):
    GET = auto()
    PUT = auto()
    PATCH = auto()
    POST = auto()
    DELETE = auto()
    OPTIONS = auto()
    TRACE = auto()


@dataclass
class LambdaEvent:
    event: dict[str, Any]
    context: LambdaContext


@dataclass
class Request(LambdaEvent):
    method: HTTPMethod
    resource: str
    path: str
    headers: MultiDict[str, str]
    query_parameters: MultiDict[str, str]
    body: str | None


@dataclass
class Response:
    body: dict[str, Any] | list[Any] | str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    status: HTTPStatus | int = HTTPStatus.OK
