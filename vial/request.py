from __future__ import annotations

from typing import Any, Optional

from vial.errors import ServerError
from vial.types import Request


class RequestContext:
    _INSTANCE: Optional[RequestContext] = None

    def __init__(self, request: Request) -> None:
        self.request = request

    def __enter__(self) -> RequestContext:
        RequestContext._INSTANCE = self
        return self

    def __exit__(self, *_: Any) -> None:
        RequestContext._INSTANCE = None

    @classmethod
    def active(cls) -> RequestContext:
        if not cls._INSTANCE:
            raise ServerError("Not currently within a request")
        return cls._INSTANCE


def get() -> Request:
    return RequestContext.active().request
