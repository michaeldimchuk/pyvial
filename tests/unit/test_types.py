from vial.types import MultiDict


class TestMultiDict:
    @staticmethod
    def test_init() -> None:
        values = MultiDict({"hello": ["there", "general kenobi"]})
        assert values["hello"] == ["there", "general kenobi"]
        assert values.get_first("hello") == "there"
