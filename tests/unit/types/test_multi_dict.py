from typing import Any, Callable, Mapping

import pytest

from vial.types import MultiDict


def test_init() -> None:
    values = MultiDict({"hello": ["there", "general kenobi"]})
    assert values["hello"] == ["there", "general kenobi"]
    assert values.get_first("hello") == "there"


def test_add() -> None:
    values: MultiDict[str, str] = MultiDict()
    values.add("hello", "world")
    assert values["hello"] == ["world"]

    values.add("hello", "goodbye")
    assert values["hello"] == ["world", "goodbye"]


def test_extend() -> None:
    values: MultiDict[str, str] = MultiDict()
    values.extend("hello", ["world"])
    assert values["hello"] == ["world"]

    values.extend("hello", ["goodbye"])
    assert values["hello"] == ["world", "goodbye"]


def test_delete() -> None:
    values = MultiDict({"hello": ["world"]})
    del values["hello"]
    assert "hello" not in values


def test_get_first() -> None:
    values = MultiDict({"hello": ["world", "goodbye"]})
    assert values.get_first("hello") == "world"
    cause = pytest.raises(KeyError, values.get_first, "goodbye")
    assert cause.value.args == ("goodbye",)


def test_iterator() -> None:
    values = MultiDict({"hello": ["world"], "goodbye": ["world"]})
    assert list(iter(values)) == ["hello", "goodbye"]


def test_length() -> None:
    values = MultiDict({"hello": ["world"], "goodbye": ["world"]})
    assert len(values) == 2

    del values["goodbye"]
    assert len(values) == 1


def test_set() -> None:
    values: MultiDict[str, str] = MultiDict()

    values["hello"] = ["world"]
    assert values["hello"] == ["world"]


@pytest.mark.parametrize("method", [str, repr])
def test_proxy_methods(method: Callable[[Mapping[str, Any]], str]) -> None:
    internal_values = {"hello": ["world"], "goodbye": ["world"]}
    values = MultiDict(internal_values)
    assert method(values) == method(internal_values)
