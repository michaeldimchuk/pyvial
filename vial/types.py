from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, Mapping, Optional, Tuple, Type, TypeVar

T = TypeVar("T")


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


class LambdaEvent:
    event: Dict[str, Any]
    context: LambdaContext

    def __init__(self, event: Dict[str, Any], context: LambdaContext) -> None:
        self.event = event
        self.context = context


@dataclass
class HTTPEvent(LambdaEvent):
    path: str
    headers: Mapping[str, str]
    body: Optional[str]


class EventType(Enum):
    value: Tuple[int, Type[LambdaEvent]]  # pylint: disable=invalid-name
    HTTP = auto(), HTTPEvent
    LAMBDA = auto(), LambdaEvent

    def construct(self, event: Dict[str, Any], context: LambdaContext) -> LambdaEvent:
        return self.value[1](event, context)


@dataclass
class LambdaHandler:
    name: str
    type: EventType
    function: Callable[[Dict[str, Any], LambdaContext], Any]
