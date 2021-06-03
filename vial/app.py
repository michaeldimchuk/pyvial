import json
from http import HTTPStatus
from typing import Any, Dict, Mapping, Type

from vial import loggers
from vial.blueprints import Blueprint
from vial.errors import MethodNotAllowedError, NotFoundError, ServerError
from vial.parsers import ParserAPI
from vial.routes import Route, RoutingAPI
from vial.types import HTTPMethod, Json, LambdaContext, Request, Response


class NativeJson:
    @staticmethod
    def dumps(value: Any) -> str:
        return json.dumps(value)

    @staticmethod
    def loads(value: str) -> Any:
        return json.loads(value)


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


class Vial(RoutingAPI, ParserAPI):

    route_resolver_class = RouteResolver

    invoker_class = RouteInvoker

    json_class: Type[Json] = NativeJson

    error_handler_class = ErrorHandler

    def __init__(self) -> None:
        super().__init__()
        self.route_resolver = self.route_resolver_class()
        self.error_handler = self.error_handler_class()
        self.invoker = self.invoker_class()
        self.json = self.json_class()
        self.logger = loggers.build(__name__)

    def register_blueprint(self, app: Blueprint) -> None:
        ParserAPI.register_parsers(self, app)
        RoutingAPI.register_routes(self, app)

    def __call__(self, event: Dict[str, Any], context: LambdaContext) -> Mapping[str, Any]:
        try:
            request = self._build_request(event, context)
            route = self.route_resolver(self.routes, request)
            response = self.invoker(route, request)
        except Exception as error:  # pylint: disable=broad-except
            self.logger.exception("Encountered uncaught exception")
            response = self.error_handler(error)
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
