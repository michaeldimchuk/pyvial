import json
from decimal import Decimal

import pytest

from vial.json import NativeJson


def test_dumps() -> None:
    data = {"hello": "world"}
    assert NativeJson.dumps(data) == json.dumps(data)


def test_loads() -> None:
    data = '{"hello": "world"}'
    assert NativeJson.loads(data) == json.loads(data)


def test_dumps_set() -> None:
    serialized_value = NativeJson.dumps({"one", "two", "three"})
    assert sorted(json.loads(serialized_value)) == sorted(["one", "two", "three"])


def test_dumps_failure() -> None:
    pytest.raises(TypeError, NativeJson.dumps, [Decimal("42.24")])
