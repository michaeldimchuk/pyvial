from decimal import Decimal
from typing import Any, Callable, Mapping
from uuid import UUID

Parser = Callable[[str], Any]


class KeywordParser:
    """
    A path parameter parser that converts string parameters into more specific types
    prior to being injected into route handler functions.
    """

    DEFAULT_PARSERS: Mapping[str, Parser] = {
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
        parser = self.parsers.get(name)
        if not parser:
            raise ValueError(f"Parser '{name}' is not registered.")
        return parser

    def register(self, name: str, parser: Parser) -> None:
        if name in self.parsers:
            raise ValueError(f"Parser for keyword {name} already exists")
        self.parsers[name] = parser
