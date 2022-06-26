from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Type
from urllib.parse import parse_qs, urlparse

from vial.app import Vial
from vial.exceptions import NotFoundError, VialError
from vial.json import Json, NativeJson
from vial.types import HTTPMethod, LambdaContext, Response


@dataclass
class Match:
    route: str
    path_params: dict[str, str]
    query_params: dict[str, list[str]]


class RouteMatcher:
    def __init__(self, routes: list[str]) -> None:
        self.routes = sorted(routes)

    def match(self, url: str) -> Match:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        path = self._remove_trailing_slash(parsed_url.path)
        return self._find_match(url, path.split("/"), query_params)

    def _find_match(self, url: str, parts: list[str], query_params: dict[str, list[str]]) -> Match:
        for route_url in self.routes:
            url_parts = route_url.split("/")
            if len(parts) != len(url_parts):
                continue

            if (path_params := self._match_path(parts, url_parts)) is not None:
                return Match(route_url, path_params, query_params)
        raise NotFoundError(VialError.ROUTE_NOT_FOUND.get(url))

    @staticmethod
    def _match_path(parts: list[str], url_parts: list[str]) -> dict[str, str] | None:
        path_params: dict[str, str] = {}
        for left, right in zip(parts, url_parts):
            if right.startswith("{") and right.endswith("}"):
                path_params[right[1:-1]] = left
                continue

            if left != right:
                return None
        return path_params

    @staticmethod
    def _remove_trailing_slash(path: str) -> str:
        if path != "/" and path.endswith("/"):
            return path[:-1]
        return path


class Gateway:

    json_class: Type[Json] = NativeJson

    def __init__(self, app: Vial) -> None:
        self.app = app
        self.json = self.json_class()
        self.matcher = RouteMatcher(list(app.routes))

    def get(self, path: str, headers: dict[str, str | list[str]] | None = None) -> Response:
        return self.request(HTTPMethod.GET, path, headers=headers)

    def post(self, path: str, body: str | None = None, headers: dict[str, str | list[str]] | None = None) -> Response:
        return self.request(HTTPMethod.POST, path, body, headers)

    def put(self, path: str, body: str | None = None, headers: dict[str, str | list[str]] | None = None) -> Response:
        return self.request(HTTPMethod.PUT, path, body, headers)

    def patch(self, path: str, body: str | None = None, headers: dict[str, str | list[str]] | None = None) -> Response:
        return self.request(HTTPMethod.PATCH, path, body, headers)

    def delete(self, path: str, headers: dict[str, str | list[str]] | None = None) -> Response:
        return self.request(HTTPMethod.DELETE, path, headers=headers)

    def request(
        self, method: HTTPMethod, path: str, body: str | None = None, headers: dict[str, str | list[str]] | None = None
    ) -> Response:
        request = self.build_request(method, path, body, headers)
        response = self.app(request, self.get_context())
        return self.build_response(response)

    def build_response(self, response: dict[str, Any]) -> Response:
        body: str | None = response["body"]
        return Response(self.json.loads(body) if body else None, response["headers"], response["statusCode"])

    def build_request(
        self,
        method: HTTPMethod,
        path: str,
        body: str | None = None,
        headers: dict[str, str | list[str]] | None = None,
    ) -> dict[str, Any]:
        match = self.matcher.match(path)
        return {
            "httpMethod": method.name,
            "resource": match.route,
            "path": path,
            "multiValueHeaders": self._build_headers(headers or {}),
            "multiValueQueryStringParameters": match.query_params,
            "pathParameters": match.path_params,
            "body": body,
        }

    @staticmethod
    def _build_headers(headers: dict[str, str | list[str]]) -> dict[str, list[str]]:
        multi_headers: dict[str, list[str]] = defaultdict(list)
        for name, value in headers.items():
            if isinstance(value, str):
                multi_headers[name].append(value)
            else:
                multi_headers[name].extend(value)
        return multi_headers

    @staticmethod
    def get_context() -> LambdaContext:
        return LambdaContext("vial-test", "1", "arn:vial-test", 128, "1", "vial-test-log", "vial-test-log")
