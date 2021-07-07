from http import HTTPStatus
from typing import Any, Dict, Mapping, Type

from vial.errors import MethodNotAllowedError, NotFoundError, ServerError
from vial.json import Json, NativeJson
from vial.loggers import LoggerFactory
from vial.middleware import CallChain, MiddlewareAPI, MiddlewareChain
from vial.parsers import ParserAPI
from vial.request import RequestContext
from vial.resources import Resource
from vial.routes import Route, RoutingAPI
from vial.types import HTTPMethod, LambdaContext, MultiDict, Request, Response


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


class ErrorHandler:

    DEFAULT_STATUSES = {
        Exception: HTTPStatus.INTERNAL_SERVER_ERROR,
        ValueError: HTTPStatus.BAD_REQUEST,
        NotImplementedError: HTTPStatus.NOT_IMPLEMENTED,
    }

    def __call__(self, error: Exception) -> Response:
        return Response({"message": str(error)}, status=self._get_status_code(error))

    def _get_status_code(self, error: Exception) -> HTTPStatus:
        if isinstance(error, ServerError):
            return error.status
        return self._get_native_status_code(error)

    def _get_native_status_code(self, error: Exception) -> HTTPStatus:
        for error_type in type(error).__mro__:
            if issubclass(error_type, Exception):
                status = self.DEFAULT_STATUSES.get(error_type)
                if status:
                    return status
        return HTTPStatus.INTERNAL_SERVER_ERROR


class Vial(RoutingAPI, ParserAPI, MiddlewareAPI):

    route_resolver_class = RouteResolver

    invoker_class = RouteInvoker

    logger_factory_class = LoggerFactory

    error_handler_class = ErrorHandler

    json_class: Type[Json] = NativeJson

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.route_resolver = self.route_resolver_class()
        self.error_handler = self.error_handler_class()
        self.invoker = self.invoker_class()
        self.json = self.json_class()
        self.logger = self.logger_factory_class.get(name)

    def register_resource(self, app: Resource) -> None:
        ParserAPI.register_parsers(self, app)
        RoutingAPI.register_routes(self, app)
        MiddlewareAPI.register_middlewares(self, app)

    def __call__(self, event: Dict[str, Any], context: LambdaContext) -> Mapping[str, Any]:
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
            return self.error_handler(e)

    def _build_invocation_chain(self, route: Route) -> CallChain:
        all_middleware = self.registered_middleware[self.name] + self.registered_middleware[route.resource]

        def route_invocation(event: Request) -> Response:
            return self.invoker(route, event)

        handler = MiddlewareChain(all_middleware[-1], route_invocation)
        for middleware in reversed(all_middleware[0:-1]):
            handler = MiddlewareChain(middleware, handler)
        return handler

    def _to_lambda_response(self, response: Response) -> Mapping[str, Any]:
        if not isinstance(response.body, str):
            body = self.json.dumps(response.body) if response.body is not None else None
        else:
            body = response.body
        return {"headers": response.headers, "statusCode": response.status, "body": body}

    @staticmethod
    def _build_request(event: Dict[str, Any], context: LambdaContext) -> Request:
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
