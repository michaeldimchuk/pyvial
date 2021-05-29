from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, Mapping

from vial import routes
from vial.errors import MethodNotSupported, ResourceNotFound
from vial.routes import Route
from vial.types import EventType, HTTPMethod, LambdaContext, LambdaHandler, T


class DecoratorAPI:
    def __init__(self) -> None:
        super().__init__()
        self.routes: Dict[str, Dict[HTTPMethod, Route]] = defaultdict(dict)
        self.handlers: Dict[str, LambdaHandler] = {}

    def post(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            self.register(path, HTTPMethod.POST, function, kwargs)
            return function

        return registrar

    def put(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            self.register(path, HTTPMethod.PUT, function, kwargs)
            return function

        return registrar

    def patch(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            self.register(path, HTTPMethod.PATCH, function, kwargs)
            return function

        return registrar

    def delete(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            self.register(path, HTTPMethod.DELETE, function, kwargs)
            return function

        return registrar

    def get(self, path: str, **kwargs: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            self.register(path, HTTPMethod.GET, function, kwargs)
            return function

        return registrar

    def route(
        self, path: str, methods: Iterable[HTTPMethod] = tuple(HTTPMethod), **kwargs: Any
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            for method in methods:
                self.register(path, method, function, kwargs)
            return function

        return registrar

    def register(self, path: str, method: HTTPMethod, function: Callable[..., T], metadata: Mapping[str, Any]) -> None:
        route = routes.build(path, method, function, metadata)
        self.routes[route.path][method] = route

    def lambda_function(self, name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        def registrar(function: Callable[..., T]) -> Callable[..., T]:
            self.handlers[name] = LambdaHandler(name, EventType.LAMBDA, function)
            return function

        return registrar


class RouteResolver:
    def __call__(self, resources: Mapping[str, Mapping[HTTPMethod, Route]], event: Mapping[str, Any]) -> Route:
        resource = event["resource"]
        defined_routes = resources.get(resource)
        if not defined_routes:
            raise ResourceNotFound(resource)

        method = HTTPMethod[event["httpMethod"]]
        route = defined_routes.get(method)
        if not route:
            raise MethodNotSupported(method.name)

        return route


class ArgumentBuilder:
    def __call__(self, route: Route, event: Mapping[str, Any]) -> Mapping[str, Any]:
        if not route.variables:
            return {}
        path_params: Mapping[str, str] = event["pathParameters"]
        args: Dict[str, Any] = {}
        for name, parser in route.variables.items():
            args[name] = parser(path_params[name])
        return args


class RouteInvoker:
    def __call__(self, function: Callable[..., Any], args: Mapping[str, Any]) -> Any:
        return function(**args)


class Vial(DecoratorAPI):

    route_resolver_class = RouteResolver

    argument_builder_class = ArgumentBuilder

    invoker_class = RouteInvoker

    def __init__(self) -> None:
        DecoratorAPI.__init__(self)

        self.route_resolver = self.route_resolver_class()
        self.argument_builder = self.argument_builder_class()
        self.invoker = self.invoker_class()

    def __call__(self, event: Dict[str, Any], context: LambdaContext) -> Any:
        route = self.route_resolver(self.routes, event)
        args = self.argument_builder(route, event)
        return self.invoker(route.function, args)

    @staticmethod
    def _default_invoker(function: Callable[..., Any], args: Mapping[str, Any]) -> Any:
        return function(**args)
