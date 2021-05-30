import json
from typing import Any, Callable, Dict, Mapping

from vial.errors import MethodNotAllowedError, NotFoundError
from vial.parsers import KeywordParser
from vial.routes import Route, RoutingAPI
from vial.types import HTTPMethod, LambdaContext, Request, Response, T


class Json:
    @staticmethod
    def dumps(value: Any) -> str:
        return json.dumps(value)

    @staticmethod
    def loads(value: str) -> Any:
        return json.loads(value)


class ParserAPI:

    parser_class = KeywordParser

    def __init__(self) -> None:
        super().__init__()
        self.param_parser = self.parser_class()

    def parser(self, name: str) -> Callable[[Callable[[str], T]], Callable[[str], T]]:
        def registration_function(function: Callable[[str], T]) -> Callable[[str], T]:
            self.register_parser(name, function)
            return function

        return registration_function

    def register_parser(self, name: str, parser: Callable[[str], T]) -> None:
        self.param_parser.register(name, parser)


class RouteResolver:
    def __call__(self, resources: Mapping[str, Mapping[HTTPMethod, Route]], request: Request) -> Route:
        defined_routes = resources.get(request.resource)
        if not defined_routes:
            raise NotFoundError(request.resource)

        route = defined_routes.get(request.method)
        if not route:
            raise MethodNotAllowedError(request.method.name)

        return route


class RouteInvoker:
    def __call__(self, route: Route, request: Request) -> Response:
        args = self._build_args(route, request)
        result = route.function(*args.values())
        return self._to_response(result)

    @staticmethod
    def _to_response(result: Any) -> Response:
        if isinstance(result, Response):
            return result
        if result is None or not isinstance(result, tuple):
            return Response(result)
        return Response(*result)

    @staticmethod
    def _build_args(route: Route, request: Request) -> Mapping[str, Any]:
        if not route.variables:
            return {}
        path_params: Mapping[str, str] = request.event["pathParameters"]
        args: Dict[str, Any] = {}
        for name, parser in route.variables.items():
            args[name] = parser(path_params[name])
        return args


class Vial(RoutingAPI, ParserAPI):

    route_resolver_class = RouteResolver

    invoker_class = RouteInvoker

    json_class = Json

    def __init__(self) -> None:
        super().__init__()
        self.route_resolver = self.route_resolver_class()
        self.invoker = self.invoker_class()
        self.json = self.json_class()

    def __call__(self, event: Dict[str, Any], context: LambdaContext) -> Mapping[str, Any]:
        request = self._build_request(event, context)
        route = self.route_resolver(self.routes, request)
        response = self.invoker(route, request)
        return self._to_lambda_response(response)

    def _to_lambda_response(self, response: Response) -> Mapping[str, Any]:
        if not isinstance(response.body, str):
            body = self.json.dumps(response.body) if response.body is not None else None
        else:
            body = response.body
        return {"headers": response.headers, "statusCode": response.status, "body": body}

    @staticmethod
    def _build_request(event: Dict[str, Any], context: LambdaContext) -> Request:
        return Request(
            HTTPMethod[event["httpMethod"]],
            event["resource"],
            event["path"],
            event["headers"],
            event["queryStringParameters"],
            event["body"],
            event,
            context,
        )
