from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

import pytest

from vial.exceptions import ServerError, VialError
from vial.parsers import KeywordParser


@pytest.mark.parametrize(
    "name, parser",
    [("str", str), ("bool", bool), ("int", int), ("float", float), ("decimal", Decimal), ("uuid", UUID)],
)
def test_default_parsers(name: str, parser: Callable[[str], Any]) -> None:
    """Mostly just a sanity check to make sure all agreed upon parsers are registered."""
    assert KeywordParser().get(name) == parser


def test_unknown_parser() -> None:
    cause = pytest.raises(ServerError, KeywordParser().get, "hello")
    assert cause.value.error.code == VialError.PARSER_NOT_REGISTERED.name


def test_register() -> None:
    parser = KeywordParser()
    cause = pytest.raises(ServerError, parser.get, "hello")
    assert cause.value.error.code == VialError.PARSER_NOT_REGISTERED.name

    parser.register("hello", set)

    assert parser.get("hello")("hello world") == set("hello world")


def test_register_already_exists() -> None:
    cause = pytest.raises(ServerError, KeywordParser().register, "str", str)
    assert cause.value.error.code == VialError.PARSER_ALREADY_EXISTS.name
