from __future__ import annotations

from collections import defaultdict
from typing import Callable, Protocol

from vial.types import Request, Response, T


class CallChain(Protocol):
    def __call__(self, event: Request) -> Response:
        pass


class MiddlewareChain:
    def __init__(self, handler: Callable[[Request, CallChain], Response], next_call: CallChain) -> None:
        self.handler = handler
        self.next_call = next_call

    def __call__(self, event: Request) -> Response:
        return self.handler(event, self.next_call)


class MiddlewareAPI:
    def __init__(self, name: str) -> None:
        super().__init__(name)  # type: ignore[call-arg] # https://github.com/python/mypy/issues/4335
        self.name = name
        self.registered_middleware: dict[str, list[Callable[[Request, CallChain], T]]] = defaultdict(list)

    def middleware(self, function: Callable[[Request, CallChain], T]) -> Callable[[Request, CallChain], T]:
        self.register_middleware(function)
        return function

    def register_middleware(self, middleware: Callable[[Request, CallChain], T]) -> None:
        self.registered_middleware[self.name].append(middleware)

    def register_middlewares(self, other: MiddlewareAPI) -> None:
        self.registered_middleware.update(other.registered_middleware)
