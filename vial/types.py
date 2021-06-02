from dataclasses import dataclass, field
from enum import Enum, auto
from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Protocol, TypeVar, Union

T = TypeVar("T")


class Json(Protocol):
    @staticmethod
    def dumps(value: Any) -> str:
        ...

    @staticmethod
    def loads(value: str) -> Any:
        ...


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
class Request:
    method: HTTPMethod
    resource: str
    path: str
    headers: Dict[str, str]
    query_parameters: Dict[str, str]
    body: Optional[str]
    event: Dict[str, Any]
    context: LambdaContext


@dataclass
class Response:
    body: Optional[Union[Mapping[str, Any], List[Any], str]] = None
    headers: Mapping[str, str] = field(default_factory=dict)
    status: Union[HTTPStatus, int] = HTTPStatus.OK
