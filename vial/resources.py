from vial.middleware import MiddlewareAPI
from vial.parsers import ParserAPI
from vial.routes import RoutingAPI


class Resource(RoutingAPI, ParserAPI, MiddlewareAPI):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
