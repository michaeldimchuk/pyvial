from typing import Any, Type

from vial.errors import ErrorHandlingAPI, MethodNotAllowedError, NotFoundError
from vial.json import Json, NativeJson
from vial.loggers import LoggerFactory
from vial.middleware import CallChain, MiddlewareAPI, MiddlewareChain
from vial.parsers import ParserAPI
from vial.request import RequestContext
from vial.resources import Resource
from vial.routes import Route, RoutingAPI
from vial.types import HTTPMethod, LambdaContext, MultiDict, Request, Response


class RouteResolver:
    def __call__(self, resources: dict[str, dict[HTTPMethod, Route]], request: Request) -> Route:
        defined_routes = resources.get(request.resource)
        if not defined_routes:
            raise NotFoundError(f"No route defined for {request.resource}")

        route = defined_routes.get(request.method)
        if not route:
            raise MethodNotAllowedError(f"No route defined for method {request.method.name}")

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
    def _build_args(route: Route, request: Request) -> dict[str, Any]:
        if not route.variables:
            return {}
        path_params: dict[str, str] = request.event["pathParameters"]
        args: dict[str, Any] = {}
        for name, parser in route.variables.items():
            args[name] = parser(path_params[name])
        return args


class Vial(RoutingAPI, ParserAPI, MiddlewareAPI, ErrorHandlingAPI):

    route_resolver_class = RouteResolver

    invoker_class = RouteInvoker

    logger_factory_class = LoggerFactory

    json_class: Type[Json] = NativeJson

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.route_resolver = self.route_resolver_class()
        self.invoker = self.invoker_class()
        self.json = self.json_class()
        self.logger = self.logger_factory_class.get(name)

    def register_resource(self, app: Resource) -> None:
        ParserAPI.register_parsers(self, app)
        RoutingAPI.register_routes(self, app)
        MiddlewareAPI.register_middlewares(self, app)

    def __call__(self, event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
        request = self._build_request(event, context)
        with RequestContext(request):
            response = self._handle_request(request)
            return self._to_lambda_response(response)

    def _handle_request(self, request: Request) -> Response:
        try:
            route = self.route_resolver(self.routes, request)
            return self._build_invocation_chain(route)(request)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.exception("Encountered uncaught exception")
            return self.default_error_handler(e)

    def _build_invocation_chain(self, route: Route) -> CallChain:
        all_middleware = self.registered_middleware[self.name] + self.registered_middleware[route.resource]

        def route_invocation(event: Request) -> Response:
            return self.invoker(route, event)

        if not all_middleware:
            return route_invocation

        handler = MiddlewareChain(all_middleware[-1], route_invocation)
        for middleware in reversed(all_middleware[0:-1]):
            handler = MiddlewareChain(middleware, handler)
        return handler

    def _to_lambda_response(self, response: Response) -> dict[str, Any]:
        if not isinstance(response.body, str):
            body = self.json.dumps(response.body) if response.body is not None else None
        else:
            body = response.body
        return {"headers": response.headers, "statusCode": response.status, "body": body}

    @staticmethod
    def _build_request(event: dict[str, Any], context: LambdaContext) -> Request:
        return Request(
            event,
            context,
            HTTPMethod[event["httpMethod"]],
            event["resource"],
            event["path"],
            MultiDict(event["multiValueHeaders"]),
            MultiDict(event["multiValueQueryStringParameters"]),
            event["body"],
        )
