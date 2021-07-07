from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Type, Union
from urllib.parse import parse_qs, urlparse

from vial.app import Vial
from vial.errors import NotFoundError
from vial.json import Json, NativeJson
from vial.types import HTTPMethod, LambdaContext, Response


@dataclass
class Match:
    route: str
    path_params: Mapping[str, str]
    query_params: Mapping[str, List[str]]


class RouteMatcher:
    def __init__(self, routes: List[str]) -> None:
        self.routes = sorted(routes)

    def match(self, url: str) -> Match:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        path = self._remove_trailing_slash(parsed_url.path)
        return self._find_match(url, path.split("/"), query_params)

    def _find_match(self, url: str, parts: List[str], query_params: Mapping[str, List[str]]) -> Match:
        for route_url in self.routes:
            url_parts = route_url.split("/")
            if len(parts) != len(url_parts):
                continue

            path_params = self._match_path(parts, url_parts)
            if path_params is not None:
                return Match(route_url, path_params, query_params)
        raise NotFoundError(f"No matching route found for {url}")

    @staticmethod
    def _match_path(parts: List[str], url_parts: List[str]) -> Optional[Mapping[str, str]]:
        path_params: Dict[str, str] = {}
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

    def get(self, path: str, headers: Optional[Mapping[str, str]] = None) -> Response:
        request = self.build_request(HTTPMethod.GET, path, None, headers)
        response = self.app(request, self.get_context())
        body: Optional[str] = response["body"]
        return Response(self.json.loads(body) if body else None, response["headers"], response["statusCode"])

    def build_request(
        self,
        method: HTTPMethod,
        path: str,
        body: Optional[str],
        headers: Optional[Mapping[str, Union[str, Sequence[str]]]] = None,
    ) -> Dict[str, Any]:
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
    def _build_headers(headers: Mapping[str, Union[str, Sequence[str]]]) -> Mapping[str, List[str]]:
        multi_headers: Mapping[str, List[str]] = defaultdict(list)
        for name, value in headers.items():
            if isinstance(value, Iterable):
                multi_headers[name].extend(value)
            else:
                multi_headers[name].append(value)
        return multi_headers

    @staticmethod
    def get_context() -> LambdaContext:
        return LambdaContext("vial-test", "1", "arn:vial-test", 128, "1", "vial-test-log", "vial-test-log")
