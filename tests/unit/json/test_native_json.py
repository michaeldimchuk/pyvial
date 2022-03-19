import dataclasses
import json
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

import pytest

from vial.json import NativeJson
from vial.types import HTTPMethod


@dataclass
class Kitchen:
    table_count: int


@dataclass
class House:
    kitchen: Kitchen
    color: str


def test_dumps() -> None:
    data = {"hello": "world"}
    assert NativeJson.dumps(data) == json.dumps(data)


def test_loads() -> None:
    data = '{"hello": "world"}'
    assert NativeJson.loads(data) == json.loads(data)


def test_dumps_set() -> None:
    serialized_value = NativeJson.dumps({"one", "two", "three"})
    assert sorted(json.loads(serialized_value)) == sorted(["one", "two", "three"])


def test_dumps_enum() -> None:
    expected_value = HTTPMethod.GET
    serialized_value = NativeJson.dumps({"value": expected_value})
    assert serialized_value == json.dumps({"value": expected_value.name})


def test_dumps_uuid() -> None:
    expected_value = uuid4()
    serialized_value = NativeJson.dumps({"value": expected_value})
    assert serialized_value == json.dumps({"value": str(expected_value)})


def test_dumps_dataclass() -> None:
    expected_value = House(Kitchen(2), "Blue")
    serialized_value = NativeJson.dumps(expected_value)
    assert serialized_value == json.dumps(dataclasses.asdict(expected_value))


def test_dumps_failure() -> None:
    pytest.raises(TypeError, NativeJson.dumps, [Decimal("42.24")])
