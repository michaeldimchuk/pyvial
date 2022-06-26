from __future__ import annotations

from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from vial.errors import ServerError, VialError
from vial.types import T

Parser = Callable[[str], Any]


class KeywordParser:
    """
    A path parameter parser that converts string parameters into more specific types
    prior to being injected into route handler functions.
    """

    DEFAULT_PARSERS: dict[str, Parser] = {
        "str": str,
        "bool": bool,
        "int": int,
        "float": float,
        "decimal": Decimal,
        "uuid": UUID,
    }

    def __init__(self) -> None:
        self.parsers = dict(self.DEFAULT_PARSERS)

    def get(self, name: str) -> Parser:
        if not (parser := self.parsers.get(name)):
            raise ServerError(VialError.PARSER_NOT_REGISTERED.get(name))
        return parser

    def register(self, name: str, parser: Parser) -> None:
        if name in self.parsers:
            raise ServerError(VialError.PARSER_ALREADY_EXISTS.get(name))
        self.parsers[name] = parser


class ParserAPI:
    parser_class = KeywordParser

    def __init__(self, name: str) -> None:
        super().__init__(name)  # type: ignore[call-arg] # https://github.com/python/mypy/issues/4335
        self.name = name
        self.param_parser = self.parser_class()

    def parser(self, name: str) -> Callable[[Callable[[str], T]], Callable[[str], T]]:
        def registration_function(function: Callable[[str], T]) -> Callable[[str], T]:
            self.register_parser(name, function)
            return function

        return registration_function

    def register_parser(self, name: str, parser: Callable[[str], T]) -> None:
        self.param_parser.register(name, parser)

    def register_parsers(self, other: ParserAPI) -> None:
        self.param_parser.parsers.update(other.param_parser.parsers)
