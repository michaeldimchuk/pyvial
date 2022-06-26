import base64
from typing import Any, Type, cast

from vial.errors import ErrorHandlingAPI
from vial.exceptions import MethodNotAllowedError, NotFoundError, VialError
from vial.json import Json, NativeJson
from vial.loggers import LoggerFactory
from vial.middleware import CallChain, MiddlewareAPI, MiddlewareChain
from vial.parsers import ParserAPI
from vial.request import RequestContext
from vial.routes import Route, RoutingAPI
from vial.types import HTTPMethod, LambdaContext, MultiDict, Request, Response


class RouteResolver:
    """
    Rudimentary resolver which tries to find a one to one mapping between the API Gateway resource
    and a route defined within the Vial application. As an example an API Gateway may have a resource
    under the "/users/{user_id}/addresses" path, which will be matched against an exact same mapping on
    Vial, but will not be matched against "/users/something/addresses".

    This approach only works when using direct routes and won't work with Proxy+ integrations, which don't
    try to match against pre-defined resources. In such a use case, this class can be overridden with a
    custom implementation and used to replace the Vial#route_resolver_class class field. For this use case,
    the vial.gateway.RouteMatcher class can be used to match conventional URLs to route resources.
    """

    def __call__(self, resources: dict[str, dict[HTTPMethod, Route]], request: Request) -> Route:
        if not (defined_routes := resources.get(request.resource)):
            raise NotFoundError(VialError.ROUTE_NOT_FOUND.get(request.resource))

        if not (route := defined_routes.get(request.method)):
            raise MethodNotAllowedError(VialError.METHOD_NOT_ALLOWED.get(request.resource, request.method.name))

        return route


class RouteInvoker:
    def __call__(self, route: Route, request: Request) -> Response:
        """
        Invokes the route function with path parameters passed in the exact same order as they
        are defined in the route. This has the advantage of being able to rename path parameters
        in code without affecting the API Gateway integration, which may not allow renames in
        certain circumstances.

        This behaviour can be modified to bind the path parameters by name to the route function
        with kwarg style parameter passing, by overriding this class and using that as the new
        value of the Vial#route_invoker_class field.
        """
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


class Resource(RoutingAPI, ParserAPI, MiddlewareAPI, ErrorHandlingAPI):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name


class Vial(RoutingAPI, ParserAPI, MiddlewareAPI, ErrorHandlingAPI):

    route_resolver_class = RouteResolver

    route_invoker_class = RouteInvoker

    logger_factory_class = LoggerFactory

    json_class: Type[Json] = NativeJson

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name
        self.route_resolver = self.route_resolver_class()
        self.invoker = self.route_invoker_class()
        self.json = self.json_class()
        self.logger = self.logger_factory_class.get(name)

    def register_resource(self, app: Resource) -> None:
        self.register_parsers(app)
        self.register_routes(app)
        self.register_middlewares(app)
        self.register_error_handlers(app)

    def __call__(self, event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
        request = self._build_request(event, context)
        with RequestContext(request):
            response = self._handle_request(request)
            return self._to_lambda_response(response)

    def _handle_request(self, request: Request) -> Response:
        route_resource = self.name  # If a route can't be found, default to the global application
        try:
            route = self.route_resolver(self.routes, request)
            route_resource = route.resource
            return self._build_invocation_chain(route)(request)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.exception("Encountered uncaught exception")
            return self.default_error_handler(route_resource, e)

    def _build_invocation_chain(self, route: Route) -> CallChain:
        def route_invocation(event: Request) -> Response:
            return self.invoker(route, event)

        if not (all_middleware := self.registered_middleware[self.name] + self.registered_middleware[route.resource]):
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

    def _build_request(self, event: dict[str, Any], context: LambdaContext) -> Request:
        return Request(
            event,
            context,
            HTTPMethod[event["httpMethod"]],
            event["resource"],
            event["path"],
            MultiDict(event["multiValueHeaders"]),
            MultiDict(event["multiValueQueryStringParameters"]),
            self._get_body(event),
        )

    @staticmethod
    def _get_body(event: dict[str, Any]) -> str:
        if event.get("isBase64Encoded"):
            return base64.b64decode(event["body"]).decode("utf-8")
        return cast(str, event["body"])
