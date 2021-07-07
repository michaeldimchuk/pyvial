from dataclasses import dataclass, field
from enum import Enum, auto
from http import HTTPStatus
from typing import Any, Dict, Iterator, List, Mapping, MutableMapping, Optional, TypeVar, Union

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class MultiDict(MutableMapping[K, List[V]]):  # pylint: disable=too-many-ancestors
    def __init__(self, values: Optional[MutableMapping[K, List[V]]] = None) -> None:
        super().__init__()
        self._values = values or {}

    def __delitem__(self, key: K) -> None:
        del self._values[key]

    def __getitem__(self, key: K) -> List[V]:
        return self._values[key]

    def get_first(self, key: K) -> V:
        return self._values[key][0]

    def extend(self, key: K, value: List[V]) -> None:
        existing_values = self._values.get(key)
        if existing_values is not None:
            existing_values.extend(value)
        else:
            self._values[key] = value

    def add(self, key: K, value: V) -> None:
        existing_values = self._values.get(key)
        if existing_values is not None:
            existing_values.append(value)
        else:
            self._values[key] = [value]

    def __iter__(self) -> Iterator[K]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __setitem__(self, key: K, value: List[V]) -> None:
        self._values[key] = value


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
    custom: Dict[str, Any]
    env: Dict[str, Any]


@dataclass
class LambdaContext:
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: Optional[CognitoIdentity] = None
    client_context: Optional[ClientContext] = None

    @staticmethod
    def get_remaining_time_in_millis() -> int:
        return 0


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
    event: Dict[str, Any]
    context: LambdaContext


@dataclass
class Request(LambdaEvent):
    method: HTTPMethod
    resource: str
    path: str
    headers: MultiDict[str, str]
    query_parameters: MultiDict[str, str]
    body: Optional[str]


@dataclass
class Response:
    body: Optional[Union[Mapping[str, Any], List[Any], str]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    status: Union[HTTPStatus, int] = HTTPStatus.OK
