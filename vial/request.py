from __future__ import annotations

from typing import Any

from vial import timestamps
from vial.exceptions import ServerError, VialError
from vial.types import Request


class RequestContext:
    _INSTANCE: RequestContext | None = None

    def __init__(self, request: Request) -> None:
        self.request = request
        self.start_time = timestamps.epoch_millis()

    @property
    def elapsed_time(self) -> float:
        return timestamps.epoch_millis() - self.start_time

    @property
    def remaining_time(self) -> int:
        return self.request.context.get_remaining_time_in_millis()

    def __enter__(self) -> RequestContext:
        RequestContext._INSTANCE = self
        return self

    def __exit__(self, *_: Any) -> None:
        RequestContext._INSTANCE = None

    @classmethod
    def active(cls) -> RequestContext:
        if not cls._INSTANCE:
            raise ServerError(VialError.NOT_IN_REQUEST.get())
        return cls._INSTANCE


def get() -> Request:
    return RequestContext.active().request


def elapsed_time() -> float:
    return RequestContext.active().elapsed_time


def remaining_time() -> int:
    return RequestContext.active().remaining_time
