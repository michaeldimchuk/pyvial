import pytest

from vial.types import LambdaContext, MultiDict


class TestMultiDict:
    @staticmethod
    def test_init() -> None:
        values = MultiDict({"hello": ["there", "general kenobi"]})
        assert values["hello"] == ["there", "general kenobi"]
        assert values.get_first("hello") == "there"

    @staticmethod
    def test_add() -> None:
        values: MultiDict[str, str] = MultiDict()
        values.add("hello", "world")
        assert values["hello"] == ["world"]

        values.add("hello", "goodbye")
        assert values["hello"] == ["world", "goodbye"]

    @staticmethod
    def test_extend() -> None:
        values: MultiDict[str, str] = MultiDict()
        values.extend("hello", ["world"])
        assert values["hello"] == ["world"]

        values.extend("hello", ["goodbye"])
        assert values["hello"] == ["world", "goodbye"]

    @staticmethod
    def test_delete() -> None:
        values = MultiDict({"hello": ["world"]})
        del values["hello"]
        assert "hello" not in values

    @staticmethod
    def test_get_first() -> None:
        values = MultiDict({"hello": ["world", "goodbye"]})
        assert values.get_first("hello") == "world"
        cause = pytest.raises(KeyError, values.get_first, "goodbye")
        assert cause.value.args == ("goodbye",)

    @staticmethod
    def test_iterator() -> None:
        values = MultiDict({"hello": ["world"], "goodbye": ["world"]})
        assert list(iter(values)) == ["hello", "goodbye"]

    @staticmethod
    def test_length() -> None:
        values = MultiDict({"hello": ["world"], "goodbye": ["world"]})
        assert len(values) == 2

        del values["goodbye"]
        assert len(values) == 1

    @staticmethod
    def test_set() -> None:
        values: MultiDict[str, str] = MultiDict()

        values["hello"] = ["world"]
        assert values["hello"] == ["world"]


class TestLambdaContext:
    @staticmethod
    def test_get_remaining_time_in_millis(context: LambdaContext) -> None:
        assert context.get_remaining_time_in_millis() == 0
