from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from vial.parsers import KeywordParser, Parser
from vial.types import HTTPMethod, T


@dataclass(frozen=True)
class Route:
    resource: str
    path: str
    method: HTTPMethod
    variables: dict[str, Parser]
    function: Callable[..., Any]
    metadata: dict[str, Any]


class RoutingAPI:
    name: str
    param_parser: KeywordParser

    def __init__(self) -> None:
        super().__init__()
        self.routes: dict[str, dict[HTTPMethod, Route]] = defaultdict(dict)

    def post(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        return self.route(path, [HTTPMethod.POST], **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        return self.route(path, [HTTPMethod.PUT], **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        return self.route(path, [HTTPMethod.PATCH], **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        return self.route(path, [HTTPMethod.DELETE], **kwargs)

    def get(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        return self.route(path, [HTTPMethod.GET], **kwargs)

    def route(
        self, path: str, methods: Iterable[HTTPMethod] = tuple(HTTPMethod), **kwargs: Any
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            for method in methods:
                self._register_route(path, method, function, kwargs)
            return function

        return registrar

    def register_routes(self, other: RoutingAPI) -> None:
        for resource, routes in other.routes.items():
            self.routes[resource].update(routes)

    def _register_route(
        self, path: str, method: HTTPMethod, function: Callable[..., T], metadata: dict[str, Any]
    ) -> None:
        route = self._build_route(path, method, function, metadata)
        self.routes[route.path][method] = route

    def _build_route(
        self, path: str, method: HTTPMethod, function: Callable[..., Any], metadata: dict[str, Any]
    ) -> Route:
        parsed_components: list[str] = []
        variables: dict[str, Parser] = {}
        self._parse_components(path.split("/"), parsed_components, variables)
        return Route(self.name, "/".join(parsed_components), method, variables, function, metadata)

    def _parse_components(
        self, components: list[str], parsed_components: list[str], variables: dict[str, Parser]
    ) -> None:
        for component in components:
            if component.startswith("{") and component.endswith("}"):
                name, parser = self._build_variable(component)
                variables[name] = parser
                parsed_components.append(f"{{{name}}}")
            else:
                parsed_components.append(component)

    def _build_variable(self, component: str) -> tuple[str, Parser]:
        placeholder = component[1:-1]
        name_and_parser = placeholder.split(":")
        if len(name_and_parser) == 1:
            return name_and_parser[0], str
        return name_and_parser[0], self.param_parser.get(name_and_parser[1])
